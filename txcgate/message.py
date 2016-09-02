#!/usr/bin/python

import math
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
import parsimonious.exceptions
import command

ParseError = parsimonious.exceptions.ParseError

LEVEL_MAX = 255

cgate_gammar = Grammar(r"""
    LINE                = (COMMAND / SECURITY_EVENT / COMMENT)? _? COMMENT?
    COMMAND             = LIGHTING_CMD / SHORT_CMD / TRIGGER_EVENT
    SECURITY_EVENT      = "#" _ SECURITY _ SECURITY_SUB_EVENT

    SHORT_CMD           = LIGHTING_SUB_CMD
    LIGHTING_CMD        = LIGHTING _ LIGHTING_SUB_CMD
    LIGHTING_SUB_CMD    = RAMP_CMD / ON_CMD / OFF_CMD
    RAMP_CMD            = RAMP _ object_identifier _ ramp_level (_ ramp_time (_ "force")?)?
    ON_CMD              = ON _ object_identifier (_ "force")?
    OFF_CMD             = OFF _ object_identifier (_ "force")?

    TRIGGER_EVENT       = TRIGGER _ EVENT _ trigger_group_address _ action_selector

    SECURITY_SUB_EVENT  = ZONE_SEALED_EVENT / ZONE_UNSEALED_EVENT / ARM_READY_EVENT / ARM_NOT_READY_EVENT
        / EXIT_DELAY_STARTED_EVENT / ENTRY_DELAY_STARTED_EVENT / SYSTEM_ARM_EVENT

    ZONE_SEALED_EVENT   = ZONE_SEALED _ group_address
    ZONE_UNSEALED_EVENT = ZONE_UNSEALED _ group_address
    ARM_READY_EVENT     = ARM_READY _ application_address
    ARM_NOT_READY_EVENT         = ARM_NOT_READY _ group_address
    EXIT_DELAY_STARTED_EVENT    = EXIT_DELAY_STARTED _ application_address
    ENTRY_DELAY_STARTED_EVENT   = ENTRY_DELAY_STARTED _ application_address
    SYSTEM_ARM_EVENT    = SYSTEM_ARM _ application_address _ arm_type

    LIGHTING        = ~"lighting"i
    RAMP            = ~"ramp"i
    ON              = ~"on"i
    OFF             = ~"off"i
    TRIGGER         = ~"trigger"i
    EVENT           = ~"event"i
    SECURITY        = ~"security"i
    ZONE_SEALED     = ~"zone_sealed"i
    ZONE_UNSEALED   = ~"zone_unsealed"i
    ARM_READY       = ~"arm_ready"i
    ARM_NOT_READY   = ~"arm_not_ready"i
    EXIT_DELAY_STARTED  = ~"exit_delay_started"i
    ENTRY_DELAY_STARTED = ~"entry_delay_started"i
    SYSTEM_ARM      = ~"system_arm"i

    object_identifier       = NAME / group_address / application_address / network_address / physical_address / project_address
    network_address         = (project_prefix / "/")? network_name
    project_prefix          = "//" project_name "/"
    project_name            = ~"\w{1,8}"i
    network_name            = DIGIT+ / NAME
    physical_address        = (project_prefix / "/")+ "p" "/" network_name "/" unit_number ("/" terminal_number)?
    unit_number             = numeric_address
    numeric_address         = DIGIT+ / ("$" HEX_DIGIT+) / "*"
    terminal_number         = numeric_address
    application_address     = (project_prefix / "/")? network_name (("/" application_number ) / "//")
    application_number      = numeric_address / "~"
    group_address           = application_address "/" group_number
    group_number            = numeric_address
    project_address         = "//" project_name
    system_address          = NAME

    ramp_level  = ~"\d{1,3}" "%"?           # in the range 0-255, or 0-100 if "%" is used
    ramp_time   = ~"\d{1,2}" ("s" / "m")?     # s for seconds, m for minutes

    trigger_group_address   = application_address "/" group_number
    action_selector         = ~"\d{1,3}" "%"?           # in the range 0-255, or 0-100 if "%" is used

    arm_type    = ~"\d{1,3}"

    COMMENT     = "#" ~".*"?

    SP          = "\x20"
    HTAB        = "\x09"
    _           = (SP / HTAB)+
    ALPHA       = ~"[A-Za-z]"
    DIGIT       = ~"[0-9]"
    HEX_DIGIT   = ~"[0-9A-F]"i
    NAME        = ALPHA ~"[\x21-\x23\x25-\x2b\x3b-\x40\x5b-\x60\x7b-\x7d0-9A-Za-z]"*
""")

class CGateVisitor(NodeVisitor):
    grammar = cgate_gammar

    visit_COMMAND = visit_SHORT_CMD = visit_LIGHTING_SUB_CMD = visit_SECURITY_SUB_EVENT = NodeVisitor.lift_child

    def generic_visit(self, node, children):
        if children:
            return children

    def visit_LINE(self, node, children):
        return children[0][0][0]

    def visit_LIGHTING_CMD(self, node, children):
        return children[2]

    def visit_SECURITY_EVENT(self, node, children):
        return children[4]

    def visit_RAMP_CMD(self, node, children):
        r = command.Ramp(children[2], children[4])
        if children[5]:
            r.time = children[5][0][1]
        return r

    def visit_ON_CMD(self, node, children):
        r = command.On(children[2])
        return r

    def visit_TRIGGER_EVENT(self, node, children):
        r = command.Trigger(children[4], children[6])
        return r

    def visit_OFF_CMD(self, node, children):
        r = command.Off(children[2])
        return r

    def visit_ZONE_SEALED_EVENT(self, node, children):
        r = command.ZoneSealed(children[2], 255)
        return r

    def visit_ZONE_UNSEALED_EVENT(self, node, children):
        r = command.ZoneSealed(children[2], 0)
        return r

    def visit_SYSTEM_ARM_EVENT(self, node, children):
        r = command.SystemArmed(children[2], children[4])
        return r

    def visit_group_address(self, node, children):
        return node.text

    def visit_arm_type(self, node, children):
        return int(node.text)

    def visit_object_identifier(self, node, children):
        return node.text

    def visit_trigger_group_address(self, node, children):
        return node.text

    def visit_application_address(self, node, children):
        return node.text

    def visit_ramp_level(self, node, children):
        if node.text.endswith('%'):
            return min(LEVEL_MAX, min(LEVEL_MAX, int(math.floor(float(node.text[:-1]) / 100.0 * (LEVEL_MAX+1)))))
        else:
            return int(node.text)

    def visit_action_selector(self, node, children):
        if node.text.endswith('%'):
            return min(LEVEL_MAX, min(LEVEL_MAX, int(math.floor(float(node.text[:-1]) / 100.0 * (LEVEL_MAX+1)))))
        else:
            return int(node.text)

    def visit_ramp_time(self, node, children):
        if node.text.endswith('s'):
            return int(node.text[:-1])
        elif node.text.endswith('m'):
            return int(node.text[:-1]) * 60
        else:
            return int(node.text)

    def visit_COMMENT(self, node, children):
        return None
