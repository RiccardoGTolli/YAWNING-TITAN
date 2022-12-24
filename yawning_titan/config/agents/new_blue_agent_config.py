from __future__ import annotations

from typing import Optional, Union

from yawning_titan.config.toolbox.core import ConfigGroup, ConfigGroupValidation
from yawning_titan.config.toolbox.groups.core import UseChancesGroup
from yawning_titan.config.toolbox.item_types.bool_item import BoolItem, BoolProperties
from yawning_titan.config.toolbox.item_types.float_item import (
    FloatItem,
    FloatProperties,
)
from yawning_titan.config.toolbox.item_types.int_item import IntItem, IntProperties
from yawning_titan.exceptions import ConfigGroupValidationError


# --- Tier 1 groups ---
class MakeNodeSafeGroup(ConfigGroup):
    """Group of values that collectively."""

    def __init__(
        self,
        doc: Optional[str] = None,
        use: Optional[bool] = False,
        increases_vulnerability: Optional[bool] = False,
        gives_random_vulnerability: Optional[bool] = False,
        vulnerability_change_during_node_patch: Optional[Union[float, int]] = None,
    ):
        self.use: BoolItem = BoolItem(
            value=use,
            doc="Blue fixes a node but does not restore it to its initial state.",
            properties=BoolProperties(allow_null=False, default=False),
        )
        self.increases_vulnerability: BoolItem = BoolItem(
            value=increases_vulnerability,
            doc="If blue fixes a node then the vulnerability score of that node increases.",
            properties=BoolProperties(allow_null=False),
        )
        self.gives_random_vulnerability: BoolItem = BoolItem(
            value=gives_random_vulnerability,
            doc="When fixing a node the vulnerability score is randomised.",
            properties=BoolProperties(allow_null=False),
        )
        self.vulnerability_change_during_node_patch: FloatItem = FloatItem(
            value=vulnerability_change_during_node_patch,
            doc="The amount that the vulnerability of a node changes when it is made safe.",
            properties=FloatProperties(
                allow_null=True,
                default=0,
                min_val=-1,
                max_val=1,
                inclusive_min=True,
                inclusive_max=True,
            ),
        )
        super().__init__(doc)

    def validate(self) -> ConfigGroupValidation:
        """Extend the parent validation with additional rules specific to this :class: `~yawning_titan.config.toolbox.core.ConfigGroup`."""
        super().validate()
        try:
            if (
                self.increases_vulnerability.value
                and self.gives_random_vulnerability.value
            ):
                msg = "Making a node safe cannot simultaneously increase the nodes vulnerability by a set amount and randomly set the vulnerability"
                raise ConfigGroupValidationError(msg)
        except ConfigGroupValidationError as e:
            self.validation.add_validation(msg, e)
        return self.validation


class DeceptiveNodeGroup(ConfigGroup):
    """The options related to the blue agents use of deceptive nodes."""

    def __init__(
        self,
        doc: Optional[str] = None,
        use: Optional[bool] = False,
        max_number: Optional[int] = 1,
        new_node_on_relocate: Optional[bool] = False,
    ):
        self.use: BoolItem = BoolItem(
            value=use,
            doc=(
                "Blue agent can place down deceptive nodes. These nodes act as just another node "
                "in the network but have a different chance of spotting attacks and always show when they are compromised."
            ),
            properties=BoolProperties(allow_null=False, default=False),
        )
        self.max_number: IntItem = IntItem(
            value=max_number,
            doc="The max number of deceptive nodes that blue can place.",
            properties=IntProperties(
                allow_null=True, default=1, min_val=1, inclusive_min=True
            ),
        )
        self.new_node_on_relocate: BoolItem = BoolItem(
            value=new_node_on_relocate,
            doc="""
            When the blue agent places a deceptive node and it has none left in stock it will "pick up"
            the first deceptive node that it used and "relocate it" When relocating a node will the stats for the node
            (such as the vulnerability and compromised status)
            be re-generated as if adding a new node or will they carry over from the "old" node.""",
            properties=BoolProperties(allow_null=True, default=False),
        )
        super().__init__(doc)

    def validate(self) -> ConfigGroupValidation:
        """Extend the parent validation with additional rules specific to this :class: `~yawning_titan.config.toolbox.core.ConfigGroup`."""
        super().validate()
        try:
            if self.use and self.max_number == 0:
                msg = "if the blue agent can use deceptive nodes then it must be able to create at least 1."
                raise ConfigGroupValidationError(msg)
        except ConfigGroupValidationError as e:
            self.validation.add_validation(msg, e)
        return self.validation


# --- Tier 2 groups ---
class BlueActionSetGroup(ConfigGroup):
    """The options related to the actions that the blue agent can perform."""

    def __init__(
        self,
        doc: Optional[str] = None,
        reduce_vulnerability: Optional[bool] = False,
        restore_node: Optional[bool] = False,
        scan: Optional[bool] = False,
        isolate_node: Optional[bool] = False,
        reconnect_node: Optional[bool] = False,
        do_nothing: Optional[bool] = False,
        make_node_safe: MakeNodeSafeGroup = MakeNodeSafeGroup(
            doc="all information relating to the process of the blue fixing a node but not restoring it to its initial state."
        ),
        deceptive_nodes: DeceptiveNodeGroup = DeceptiveNodeGroup(
            doc=(
                "all information relating to the blue agent placing down deceptive nodes."
                "These nodes act as just another node in the network but have a "
                "different chance of spotting attacks and always show when they "
                "are compromised."
            )
        ),
    ):
        self.reduce_vulnerability: BoolItem = BoolItem(
            value=reduce_vulnerability,
            doc="Blue picks a node and reduces the vulnerability score.",
            properties=BoolProperties(allow_null=True, default=False),
        )
        self.restore_node: BoolItem = BoolItem(
            value=restore_node,
            doc="Blue picks a node and restores everything about the node to its starting state.",
            properties=BoolProperties(allow_null=True, default=False),
        )
        self.scan: BoolItem = BoolItem(
            value=scan,
            doc="Blue scans all the nodes to try and detect any red intrusions.",
            properties=BoolProperties(allow_null=True, default=False),
        )
        self.isolate_node: BoolItem = BoolItem(
            value=isolate_node,
            doc="Blue disables all the connections to and from a node.",
            properties=BoolProperties(allow_null=True, default=False),
        )
        self.reconnect_node: BoolItem = BoolItem(
            value=reconnect_node,
            doc="Blue re-connects all the connections to and from a node.",
            properties=BoolProperties(allow_null=True, default=False),
        )
        self.do_nothing: BoolItem = BoolItem(
            value=do_nothing,
            doc="The blue agent is able to perform no attack for a given turn.",
            properties=BoolProperties(allow_null=True, default=False),
        )
        self.make_node_safe = make_node_safe
        self.deceptive_nodes = deceptive_nodes
        super().__init__(doc)

    def validate(self) -> ConfigGroupValidation:
        """Extend the parent validation with additional rules specific to this :class: `~yawning_titan.config.toolbox.core.ConfigGroup`."""
        super().validate()

        pair = [self.isolate_node.value, self.reconnect_node.value]
        try:
            if any(v is True for v in pair) and not all(v is True for v in pair):
                msg = "Blue should be able to reconnect or isolate nodes if the other is true."
                raise ConfigGroupValidationError(msg)
        except ConfigGroupValidationError as e:
            self.validation.add_validation(msg, e)


class BlueIntrusionDiscoveryGroup(ConfigGroup):
    """The options related to the ability for the blue agent to discover the red agents intrusions into the network."""

    def __init__(
        self,
        doc: Optional[str] = None,
        immediate: Optional[Union[int, float]] = None,
        immediate_deceptive_node: Optional[Union[int, float]] = None,
        on_scan: Optional[Union[int, float]] = None,
        on_scan_deceptive_node: Optional[Union[int, float]] = None,
    ):
        self.immediate = FloatItem(
            doc="Chance for blue to discover a node that red has compromised the instant red compromises the node.",
            value=immediate,
            properties=FloatProperties(
                allow_null=True,
                default=0.5,
                min_val=0,
                max_val=1,
                inclusive_min=True,
                inclusive_max=True,
            ),
        )
        self.immediate_deceptive_node = FloatItem(
            doc="Chance for blue to discover a deceptive node that red has compromised the instant it is compromised.",
            value=immediate_deceptive_node,
            properties=FloatProperties(
                allow_null=True,
                default=0.5,
                min_val=0,
                max_val=1,
                inclusive_min=True,
                inclusive_max=True,
            ),
        )
        self.on_scan = FloatItem(
            doc="When blue performs the scan action this is the chance that a red intrusion is discovered.",
            value=on_scan,
            properties=FloatProperties(
                allow_null=True,
                default=0.5,
                min_val=0,
                max_val=1,
                inclusive_min=True,
                inclusive_max=True,
            ),
        )
        self.on_scan_deceptive_node = FloatItem(
            doc="When blue uses the scan action what is the chance that blue will detect an intrusion in a deceptive node.",
            value=on_scan_deceptive_node,
            properties=FloatProperties(
                allow_null=True,
                default=0.5,
                min_val=0,
                max_val=1,
                inclusive_min=True,
                inclusive_max=True,
            ),
        )
        super().__init__(doc)

    def validate(self) -> ConfigGroupValidation:
        """Extend the parent validation with additional rules specific to this :class: `~yawning_titan.config.toolbox.core.ConfigGroup`."""
        super().validate()
        try:
            if (self.on_scan_deceptive_node.value <= self.on_scan.value) and (
                self.on_scan_deceptive_node.value != 1
            ):
                msg = "there should be a higher chance at detecting intrusions on deceptive nodes than regular nodes."
                raise ConfigGroupValidationError(msg)
        except ConfigGroupValidationError as e:
            self.validation.add_validation(msg, e)
        return self.validation


class BlueAttackDiscoveryGroup(ConfigGroup):
    """The options related to the blue agents ability to discover the attacks the red agent makes to nodes within the network."""

    def __init__(
        self,
        doc: Optional[str] = None,
        failed_attacks: UseChancesGroup = UseChancesGroup(
            doc="Whether the blue can discover failed attacks and the associated chance of discovery."
        ),
        succeeded_attacks: UseChancesGroup = UseChancesGroup(
            doc="Whether the blue can discover succeeded attacks where the nature of the compromise is known and the associated chance of discovery."
        ),
        succeeded_attacks_unknown_comprimise: UseChancesGroup = UseChancesGroup(
            doc="Whether the blue can discover succeeded attacks where the nature of the compromise is unknown and the associated chance of discovery."
        ),
    ):
        self.failed_attacks = failed_attacks
        self.succeeded_attacks_unknown_comprimise = succeeded_attacks_unknown_comprimise
        self.succeeded_attacks = succeeded_attacks

        # assign a shared link to 'chance_to_discover_succeeded_attack_deceptive_node' as this
        self.succeeded_attacks.chance.deceptive_node = (
            self.succeeded_attacks_unknown_comprimise.chance.deceptive_node
        )
        super().__init__(doc)


# --- Tier 3 groups ---


class Blue(ConfigGroup):
    """All options relating to the behavior of the blue agent."""

    def __init__(
        self,
        doc: Optional[str] = None,
        action_set: BlueActionSetGroup = BlueActionSetGroup(
            doc="The set of actions the blue agent can perform and their associated information."
        ),
        intrusion_discovery_chance: BlueIntrusionDiscoveryGroup = BlueIntrusionDiscoveryGroup(
            doc="The chances of blue discovering intrusions for different node types."
        ),
        attack_discovery: BlueAttackDiscoveryGroup = BlueAttackDiscoveryGroup(
            doc="Which of reds attacks can the blue agent discover together with their associated discovery chances for different node types."
        ),
    ):
        self.action_set = action_set
        self.intrusion_discovery_chance = intrusion_discovery_chance
        self.attack_discovery = attack_discovery
        super().__init__(doc)

    def validate(self) -> ConfigGroupValidation:
        """Extend the parent validation with additional rules specific to this :class: `~yawning_titan.config.toolbox.core.ConfigGroup`."""
        super().validate()
        try:
            if (
                self.action_set.scan.value
                and self.intrusion_discovery_chance.immediate.value == 1
            ):
                msg = (
                    "The scan action is selected yet blue has 100% chance to spot "
                    "detections. There is no need for the blue to have the scan "
                    "action in this case."
                )
                raise ConfigGroupValidationError(msg)
            elif (
                not self.action_set.scan.value
                and self.intrusion_discovery_chance.immediate.value != 1
            ):
                msg = (
                    "If the blue agent cannot scan nodes then it should be able to "
                    "automatically detect the intrusions."
                )
                raise ConfigGroupValidationError(msg)
        except ConfigGroupValidationError as e:
            self.validation.add_validation(msg, e)
        return self.validation


# action_set = BlueActionSetGroup()
# action_set.set_from_dict({
#     "restore_node": True,
#     "make_node_safe": True,
#     "scan": True,
#     "isolate_node": True,
#     "reconnect_node": True,
#     "make_node_safe":{
#         "use": True,
#         "increases_vulnerability": True,
#         "gives_random_vulnerability": True,
#         "vulnerability_change_during_node_patch": 0.5
#     }
# })
# action_set.validation.log()

# intrusions = BlueIntrusionDiscoveryGroup()
# intrusions.set_from_dict({
#     "immediate": -10,
#     "immediate_deceptive_node": -9,
#     "on_scan": "0",
#     "on_scan_deceptive_node": 0
# })
# intrusions.validation.log()

# use_chance = UseChancesGroup()
# use_chance.set_from_dict({
#     "use": True,
#     "chance":{
#         "standard_node": -0.5,
#         "deceptive_node": -0.5
#     }
# })
# use_chance.validation.log()

# attack_discovery = BlueAttackDiscoveryGroup()
# attack_discovery.set_from_dict(
#     {
#         "failed_attacks": {
#             "use": True,
#             "chance": {"standard_node": -0.5, "deceptive_node": -0.5},
#         },
#         "succeeded_attacks": {
#             "use": True,
#             "chance": {"standard_node": -0.5, "deceptive_node": -0.5},
#         },
#         "succeeded_attacks_unknown_comprimise": {"use": True, "chance": -0.4},
#     }
# )
# # print(attack_discovery.failed_attacks.chance.standard_node.value)
# attack_discovery.validation.log("attack discovery")

# blue = Blue()
# blue.set_from_dict(
#     {
#         "action_set": {
#             "restore_node": True,
#             "scan": True,
#             "isolate_node": True,
#             "reconnect_node": True,
#             "make_node_safe": {
#                 "use": True,
#                 "increases_vulnerability": True,
#                 "gives_random_vulnerability": True,
#                 "vulnerability_change_during_node_patch": 0.5,
#             },
#             "deceptive_nodes": {
#                 "use": True,
#                 "max_number": 2,
#                 "new_node_on_relocate": False,
#             },
#         },
#         "intrusion_discovery_chance": {
#             "immediate": 0,
#             "immediate_deceptive_node": 0,
#             "on_scan": 0,
#             "on_scan_deceptive_node": 0,
#         },
#         "attack_discovery": {
#             "failed_attacks": {
#                 "use": True,
#                 "chance": {"standard_node": 0.5, "deceptive_node": 0.5},
#             },
#             "succeeded_attacks": {
#                 "use": True,
#                 "chance": {"standard_node": 0.5, "deceptive_node": 0.5},
#             },
#             "succeeded_attacks_unknown_comprimise": {"use": True, "chance": 0.4},
#         },
#     }
# )
# blue.validation.log("Blue")

# print(
#     "A",
#     blue.attack_discovery.succeeded_attacks.chance.deceptive_node.value,
#     blue.attack_discovery.succeeded_attacks_unknown_comprimise.chance.deceptive_node.value,
# )
# blue.attack_discovery.succeeded_attacks.chance.deceptive_node.value = 0.6
# print(
#     "B",
#     blue.attack_discovery.succeeded_attacks.chance.deceptive_node.value,
#     blue.attack_discovery.succeeded_attacks_unknown_comprimise.chance.deceptive_node.value,
# )
