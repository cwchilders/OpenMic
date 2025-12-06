#!/usr/bin/env python3
"""
ToneX Parameter Reference Model
Comprehensive reference for the 8 tone blocks with parameter descriptions and data types
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum


class DataType(Enum):
    """Parameter data types from schema"""
    TINYINT = "tinyint(10)"
    FLOAT = "float(24)"
    INT = "int"
    VARCHAR32 = "varchar(32)"
    VARCHAR64 = "varchar(64)"
    DATE = "date"


@dataclass
class Parameter:
    """Individual parameter definition"""
    name: str
    data_type: DataType
    description: str
    value_range: str = ""
    notes: str = ""


class ToneBlock:
    """Base class for tone processing blocks"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.parameters: List[Parameter] = []

    def add_param(self, name: str, data_type: DataType, description: str,
                  value_range: str = "", notes: str = ""):
        """Add a parameter to this tone block"""
        self.parameters.append(Parameter(name, data_type, description, value_range, notes))

    def get_param_dict(self) -> Dict[str, Any]:
        """Return parameters as a dictionary"""
        return {
            'block_name': self.name,
            'block_description': self.description,
            'parameters': [
                {
                    'name': p.name,
                    'type': p.data_type.value,
                    'description': p.description,
                    'range': p.value_range,
                    'notes': p.notes
                }
                for p in self.parameters
            ]
        }


# ============================================================================
# METADATA BLOCK
# ============================================================================
metadata_block = ToneBlock(
    "Metadata",
    "Preset identification and organizational tags"
)

metadata_block.add_param("GUID", DataType.VARCHAR32,
    "Globally Unique Identifier for this preset",
    "32-character hex string")

metadata_block.add_param("Version", DataType.TINYINT,
    "Preset format version",
    "Usually 3", "Default: 1")

metadata_block.add_param("ToneModel_GUID", DataType.VARCHAR32,
    "Reference to the amp model tone capture",
    "32-character hex string")

metadata_block.add_param("OptionalToneModel_GUID", DataType.VARCHAR32,
    "Optional secondary tone model for blending",
    "32-character hex string or empty")

metadata_block.add_param("Tag_PresetName", DataType.VARCHAR32,
    "Display name of the preset (PRIMARY KEY)",
    "Max 32 chars", "Must be unique")

metadata_block.add_param("Tag_UserName", DataType.VARCHAR32,
    "Name of preset creator/user",
    "Max 32 chars")

metadata_block.add_param("Tag_ModelerTags", DataType.VARCHAR32,
    "Custom tags for organization",
    "Max 32 chars")

metadata_block.add_param("Tag_Date", DataType.DATE,
    "Creation/modification date",
    "ISO date format")

metadata_block.add_param("Tag_ModelCategory", DataType.VARCHAR32,
    "Amp category classification",
    "CLEAN, DRIVE, CRUNCH, FUZZY, etc.")

metadata_block.add_param("Tag_Instrument", DataType.VARCHAR32,
    "Target instrument type",
    "Electric Guitar, Bass, etc.")

metadata_block.add_param("Tag_InstrumentType", DataType.VARCHAR32,
    "Specific instrument model",
    "Solid Body, Semi-Hollow, etc.")

metadata_block.add_param("Tag_PickupPosition", DataType.VARCHAR32,
    "Guitar pickup selector position",
    "Bridge, Neck, Middle, None")

metadata_block.add_param("Tag_PickupType", DataType.VARCHAR32,
    "Pickup configuration",
    "H-H (LP), S-S-S, H-S-H, etc.")

metadata_block.add_param("Tag_Artist", DataType.VARCHAR32,
    "Associated artist name",
    "Max 32 chars")

metadata_block.add_param("Tag_Album", DataType.VARCHAR32,
    "Associated album name",
    "Max 32 chars")

metadata_block.add_param("Tag_Song", DataType.VARCHAR32,
    "Associated song title",
    "Max 32 chars")

metadata_block.add_param("Tag_SongPart", DataType.VARCHAR32,
    "Song section reference",
    "Verse, Chorus, Solo, etc.")

metadata_block.add_param("Tag_Genre", DataType.VARCHAR32,
    "Musical genre classification",
    "Rock, Jazz, Metal, Blues, etc.")

metadata_block.add_param("Tag_Description", DataType.VARCHAR64,
    "Preset description or notes",
    "Max 64 chars")


# ============================================================================
# AMP MODEL BLOCK
# ============================================================================
amp_model_block = ToneBlock(
    "Amp Model",
    "Core amplifier tone and gain staging controls"
)

amp_model_block.add_param("ModelEnable", DataType.TINYINT,
    "Enable/bypass the amp model",
    "0=off, 1=on")

amp_model_block.add_param("ModelMix", DataType.FLOAT,
    "Wet/dry blend of processed signal",
    "0.0-100.0%", "100% = fully processed tone")

amp_model_block.add_param("ModelGain", DataType.FLOAT,
    "Input gain/drive amount",
    "0.0-10.0", "Controls amp saturation/distortion")

amp_model_block.add_param("ModelVolume", DataType.FLOAT,
    "Output level/master volume",
    "0.0-10.0", "Final amp output level")

amp_model_block.add_param("PwrAmpEqPresence", DataType.FLOAT,
    "Power amp presence control (high-end clarity)",
    "0.0-10.0", "Adds brightness and air")

amp_model_block.add_param("PwrAmpEqDepth", DataType.FLOAT,
    "Power amp resonance/depth (low-end)",
    "0.0-10.0", "Adds bass response and thump")

amp_model_block.add_param("BPM", DataType.FLOAT,
    "Tempo reference for time-based effects",
    "20.0-999.0 BPM", "Used for sync'ed delays/modulation")


# ============================================================================
# EQ BLOCK
# ============================================================================
eq_block = ToneBlock(
    "EQ",
    "3-band parametric equalizer with frequency control"
)

eq_block.add_param("EqPost", DataType.TINYINT,
    "EQ placement in signal chain",
    "0=pre-amp, 1=post-amp", "Affects tonal character significantly")

eq_block.add_param("EqBass", DataType.FLOAT,
    "Bass boost/cut amount",
    "-10.0 to +10.0 dB", "Low frequency control")

eq_block.add_param("EqBassFreq", DataType.FLOAT,
    "Bass center frequency",
    "20.0-2000.0 Hz", "Typical: 80-400 Hz")

eq_block.add_param("EqMid", DataType.FLOAT,
    "Midrange boost/cut amount",
    "-10.0 to +10.0 dB", "Most critical for tone shaping")

eq_block.add_param("EqMidQ", DataType.FLOAT,
    "Midrange bandwidth/Q factor",
    "0.1-10.0", "Lower Q = wider, Higher Q = narrower")

eq_block.add_param("EqMidFreq", DataType.FLOAT,
    "Midrange center frequency",
    "200.0-5000.0 Hz", "Typical: 500-2000 Hz")

eq_block.add_param("EqTreble", DataType.FLOAT,
    "Treble boost/cut amount",
    "-10.0 to +10.0 dB", "High frequency control")

eq_block.add_param("EqTrebleFreq", DataType.FLOAT,
    "Treble center frequency",
    "1000.0-20000.0 Hz", "Typical: 2000-8000 Hz")


# ============================================================================
# COMPRESSION BLOCK
# ============================================================================
compression_block = ToneBlock(
    "Compression",
    "Dynamic range compression for sustain and level control"
)

compression_block.add_param("CompPost", DataType.TINYINT,
    "Compressor placement in signal chain",
    "0=pre-amp, 1=post-amp")

compression_block.add_param("CompEnable", DataType.TINYINT,
    "Enable/bypass compressor",
    "0=off, 1=on")

compression_block.add_param("CompThreshold", DataType.FLOAT,
    "Compression threshold level",
    "-60.0 to 0.0 dB", "Signals above this level are compressed")

compression_block.add_param("CompMakeUp", DataType.FLOAT,
    "Make-up gain after compression",
    "-20.0 to +20.0 dB", "Compensates for volume reduction")

compression_block.add_param("CompAttack", DataType.FLOAT,
    "Attack time (how quickly compression engages)",
    "0.1-100.0 ms", "Faster = more pick attack reduction")


# ============================================================================
# NOISE GATE BLOCK
# ============================================================================
noise_gate_block = ToneBlock(
    "Noise Gate",
    "Noise reduction and signal gating"
)

noise_gate_block.add_param("NoiseGatePost", DataType.TINYINT,
    "Noise gate placement in signal chain",
    "0=pre-amp, 1=post-amp", "Post is typical for high-gain")

noise_gate_block.add_param("NoiseGateEnable", DataType.TINYINT,
    "Enable/bypass noise gate",
    "0=off, 1=on")

noise_gate_block.add_param("NoiseGateThreshold", DataType.FLOAT,
    "Gate threshold level",
    "-100.0 to 0.0 dB", "Signals below this are attenuated")

noise_gate_block.add_param("NoiseGateRelease", DataType.FLOAT,
    "Release time (how quickly gate closes)",
    "0.0-1000.0 ms", "Longer = more natural decay")

noise_gate_block.add_param("NoiseGateDepth", DataType.FLOAT,
    "Attenuation amount when gate is closed",
    "-100.0 to 0.0 dB", "How much noise is reduced")


# ============================================================================
# MODULATION BLOCK
# ============================================================================
modulation_block = ToneBlock(
    "Modulation",
    "Chorus, tremolo, phaser, flanger, and rotary effects"
)

# Common modulation parameters
modulation_block.add_param("ModPost", DataType.TINYINT,
    "Modulation placement in signal chain",
    "0=pre-amp, 1=post-amp")

modulation_block.add_param("ModEnable", DataType.TINYINT,
    "Enable/bypass modulation effect",
    "0=off, 1=on")

modulation_block.add_param("ModModel", DataType.TINYINT,
    "Modulation effect type selector",
    "0=chorus, 1=tremolo, 2=phaser, 3=flanger, 4=rotary")

# Chorus parameters
modulation_block.add_param("ModChorusSync", DataType.TINYINT,
    "Sync chorus rate to BPM",
    "0=off, 1=on")

modulation_block.add_param("ModChorusTS", DataType.TINYINT,
    "Chorus time signature division",
    "0-15", "For tempo sync (quarter, eighth, etc.)")

modulation_block.add_param("ModChorusRate", DataType.FLOAT,
    "Chorus modulation speed",
    "0.0-20.0 Hz", "LFO rate")

modulation_block.add_param("ModChorusDepth", DataType.FLOAT,
    "Chorus modulation depth",
    "0.0-100.0%", "Amount of pitch variation")

modulation_block.add_param("ModChorusLevel", DataType.FLOAT,
    "Chorus effect mix level",
    "0.0-100.0%", "Wet signal amount")

# Tremolo parameters
modulation_block.add_param("ModTremoloSync", DataType.TINYINT,
    "Sync tremolo rate to BPM",
    "0=off, 1=on")

modulation_block.add_param("ModTremoloTS", DataType.TINYINT,
    "Tremolo time signature division",
    "0-15")

modulation_block.add_param("ModTremoloRate", DataType.FLOAT,
    "Tremolo modulation speed",
    "0.0-20.0 Hz", "Volume oscillation rate")

modulation_block.add_param("ModTremoloShape", DataType.FLOAT,
    "Tremolo waveform shape",
    "0.0-100.0%", "Sine to square wave")

modulation_block.add_param("ModTremoloSpread", DataType.FLOAT,
    "Tremolo stereo spread",
    "0.0-100.0%", "Stereo width")

modulation_block.add_param("ModTremoloLevel", DataType.FLOAT,
    "Tremolo effect intensity",
    "0.0-100.0%", "Modulation depth")

# Phaser parameters
modulation_block.add_param("ModPhaserSync", DataType.TINYINT,
    "Sync phaser rate to BPM",
    "0=off, 1=on")

modulation_block.add_param("ModPhaserTS", DataType.TINYINT,
    "Phaser time signature division",
    "0-15")

modulation_block.add_param("ModPhaserRate", DataType.FLOAT,
    "Phaser sweep speed",
    "0.0-20.0 Hz", "LFO rate")

modulation_block.add_param("ModPhaserDepth", DataType.FLOAT,
    "Phaser sweep range",
    "0.0-100.0%", "Frequency sweep amount")

modulation_block.add_param("ModPhaserLevel", DataType.FLOAT,
    "Phaser effect mix level",
    "0.0-100.0%")

# Flanger parameters
modulation_block.add_param("ModFlangerSync", DataType.TINYINT,
    "Sync flanger rate to BPM",
    "0=off, 1=on")

modulation_block.add_param("ModFlangerTS", DataType.TINYINT,
    "Flanger time signature division",
    "0-15")

modulation_block.add_param("ModFlangerRate", DataType.FLOAT,
    "Flanger sweep speed",
    "0.0-20.0 Hz")

modulation_block.add_param("ModFlangerDepth", DataType.FLOAT,
    "Flanger delay modulation depth",
    "0.0-100.0%")

modulation_block.add_param("ModFlangerFeedback", DataType.FLOAT,
    "Flanger resonance/feedback",
    "0.0-100.0%", "Increases jet-plane effect")

modulation_block.add_param("ModFlangerLevel", DataType.FLOAT,
    "Flanger effect mix level",
    "0.0-100.0%")

# Rotary (Leslie) parameters
modulation_block.add_param("ModRotarySync", DataType.TINYINT,
    "Sync rotary speed to BPM",
    "0=off, 1=on")

modulation_block.add_param("ModRotaryTS", DataType.TINYINT,
    "Rotary time signature division",
    "0-15")

modulation_block.add_param("ModRotarySpeed", DataType.FLOAT,
    "Rotary speaker speed",
    "0.0-1000.0 RPM", "Simulates fast/slow switch")

modulation_block.add_param("ModRotaryRadius", DataType.FLOAT,
    "Rotary speaker horn radius",
    "0.0-200.0", "Affects doppler shift")

modulation_block.add_param("ModRotarySpread", DataType.FLOAT,
    "Rotary stereo spread",
    "0.0-100.0%")

modulation_block.add_param("ModRotaryLevel", DataType.FLOAT,
    "Rotary effect mix level",
    "0.0-100.0%")


# ============================================================================
# DELAY BLOCK
# ============================================================================
delay_block = ToneBlock(
    "Delay",
    "Digital and tape echo effects"
)

delay_block.add_param("DelayPost", DataType.TINYINT,
    "Delay placement in signal chain",
    "0=pre-amp, 1=post-amp", "Post is standard")

delay_block.add_param("DelayEnable", DataType.TINYINT,
    "Enable/bypass delay",
    "0=off, 1=on")

delay_block.add_param("DelayModel", DataType.TINYINT,
    "Delay type selector",
    "0=digital, 1=tape", "Tape adds warmth and saturation")

# Digital delay parameters
delay_block.add_param("DelayDigitalSync", DataType.TINYINT,
    "Sync digital delay to BPM",
    "0=off, 1=on")

delay_block.add_param("DelayDigitalTS", DataType.TINYINT,
    "Digital delay time signature division",
    "0-15", "Quarter, eighth, dotted, etc.")

delay_block.add_param("DelayDigitalTime", DataType.FLOAT,
    "Digital delay time",
    "0.0-2000.0 ms", "Echo spacing")

delay_block.add_param("DelayDigitalFeedback", DataType.FLOAT,
    "Digital delay feedback/repeats",
    "0.0-100.0%", "Number of echoes")

delay_block.add_param("DelayDigitalMode", DataType.TINYINT,
    "Digital delay mode",
    "0-9", "Mono, stereo, ping-pong variations")

delay_block.add_param("DelayDigitalMix", DataType.FLOAT,
    "Digital delay wet/dry mix",
    "0.0-100.0%", "Effect level")

# Tape delay parameters
delay_block.add_param("DelayTapeSync", DataType.TINYINT,
    "Sync tape delay to BPM",
    "0=off, 1=on")

delay_block.add_param("DelayTapeTS", DataType.TINYINT,
    "Tape delay time signature division",
    "0-15")

delay_block.add_param("DelayTapeTime", DataType.FLOAT,
    "Tape delay time",
    "0.0-2000.0 ms")

delay_block.add_param("DelayTapeFeedback", DataType.FLOAT,
    "Tape delay feedback/repeats",
    "0.0-100.0%", "With tape saturation")

delay_block.add_param("DelayTapeMode", DataType.TINYINT,
    "Tape delay mode",
    "0-9", "Various tape head configurations")

delay_block.add_param("DelayTapeMix", DataType.FLOAT,
    "Tape delay wet/dry mix",
    "0.0-100.0%")


# ============================================================================
# REVERB BLOCK
# ============================================================================
reverb_block = ToneBlock(
    "Reverb",
    "Spring, room, and plate reverb effects"
)

reverb_block.add_param("ReverbPosition", DataType.TINYINT,
    "Reverb placement in signal chain",
    "0=pre-amp, 1=post-amp", "Post is standard")

reverb_block.add_param("ReverbEnable", DataType.TINYINT,
    "Enable/bypass reverb",
    "0=off, 1=on")

reverb_block.add_param("ReverbModel", DataType.INT,
    "Reverb type selector",
    "4=spring, 5=room, 6=plate", "Different reverb algorithms")

# Spring reverb parameters (4 spring models)
for i in range(1, 5):
    reverb_block.add_param(f"ReverbSpring{i}Time", DataType.FLOAT,
        f"Spring {i} reverb decay time",
        "0.0-10.0 seconds", "How long reverb tail lasts")

    reverb_block.add_param(f"ReverbSpring{i}PreDelay", DataType.FLOAT,
        f"Spring {i} pre-delay time",
        "0.0-200.0 ms", "Gap before reverb starts")

    reverb_block.add_param(f"ReverbSpring{i}Color", DataType.FLOAT,
        f"Spring {i} tone color (damping)",
        "-10.0 to +10.0", "Darker to brighter")

    reverb_block.add_param(f"ReverbSpring{i}Mix", DataType.FLOAT,
        f"Spring {i} wet/dry mix",
        "0.0-100.0%", "Effect level")

# Room reverb parameters
reverb_block.add_param("ReverbRoomTime", DataType.FLOAT,
    "Room reverb decay time",
    "0.0-10.0 seconds", "Room size simulation")

reverb_block.add_param("ReverbRoomPreDelay", DataType.FLOAT,
    "Room reverb pre-delay time",
    "0.0-200.0 ms")

reverb_block.add_param("ReverbRoomColor", DataType.FLOAT,
    "Room reverb tone color",
    "-10.0 to +10.0")

reverb_block.add_param("ReverbRoomMix", DataType.FLOAT,
    "Room reverb wet/dry mix",
    "0.0-100.0%")

# Plate reverb parameters
reverb_block.add_param("ReverbPlateTime", DataType.FLOAT,
    "Plate reverb decay time",
    "0.0-10.0 seconds", "Smooth, dense reverb")

reverb_block.add_param("ReverbPlatePreDelay", DataType.FLOAT,
    "Plate reverb pre-delay time",
    "0.0-200.0 ms")

reverb_block.add_param("ReverbPlateColor", DataType.FLOAT,
    "Plate reverb tone color",
    "-10.0 to +10.0")

reverb_block.add_param("ReverbPlateMix", DataType.FLOAT,
    "Plate reverb wet/dry mix",
    "0.0-100.0%")


# ============================================================================
# CABINET BLOCK
# ============================================================================
cabinet_block = ToneBlock(
    "Cabinet",
    "Speaker cabinet simulation and microphone modeling"
)

cabinet_block.add_param("CabType", DataType.INT,
    "Cabinet simulation type",
    "0=VIR (Virtual), 2=Classic", "VIR is more advanced modeling")

cabinet_block.add_param("VIRCabModel", DataType.INT,
    "VIR cabinet model selection",
    "0-99", "Different speaker cabinet types")

cabinet_block.add_param("VIRCabMic1Model", DataType.INT,
    "Microphone 1 model type",
    "0-50", "SM57, condenser, ribbon, etc.")

cabinet_block.add_param("VIRCabMic1X", DataType.FLOAT,
    "Microphone 1 horizontal position",
    "-2.0 to +2.0", "Off-axis to on-axis placement")

cabinet_block.add_param("VIRCabMic1Z", DataType.FLOAT,
    "Microphone 1 distance from speaker",
    "0.0-10.0", "Close-mic to room-mic")

cabinet_block.add_param("VIRCabMic2Model", DataType.INT,
    "Microphone 2 model type",
    "0-50", "For dual-mic setups")

cabinet_block.add_param("VIRCabMic2X", DataType.FLOAT,
    "Microphone 2 horizontal position",
    "-2.0 to +2.0")

cabinet_block.add_param("VIRCabMic2Z", DataType.FLOAT,
    "Microphone 2 distance from speaker",
    "0.0-10.0")

cabinet_block.add_param("VIRCabMicBlend", DataType.FLOAT,
    "Blend between microphone 1 and 2",
    "0.0-100.0%", "0% = all mic 1, 100% = all mic 2")

cabinet_block.add_param("VIRCabResonance", DataType.FLOAT,
    "Cabinet resonance/air movement",
    "0.0-10.0", "Low-end cabinet thump")


# ============================================================================
# OTHER PARAMETERS
# ============================================================================
other_block = ToneBlock(
    "Other",
    "Additional preset settings"
)

other_block.add_param("HW_ExtControllerEnable", DataType.TINYINT,
    "Enable external hardware controller integration",
    "0=off, 1=on", "For MIDI/expression pedal control")

other_block.add_param("Favorite", DataType.TINYINT,
    "Mark preset as favorite",
    "0=no, 1=yes", "For quick access/filtering")


# ============================================================================
# MASTER MODEL - ALL 8 TONE BLOCKS
# ============================================================================
class ToneXPresetModel:
    """Complete ToneX preset parameter model"""

    def __init__(self):
        self.blocks = {
            'metadata': metadata_block,
            'amp_model': amp_model_block,
            'eq': eq_block,
            'compression': compression_block,
            'noise_gate': noise_gate_block,
            'modulation': modulation_block,
            'delay': delay_block,
            'reverb': reverb_block,
            'cabinet': cabinet_block,
            'other': other_block
        }

    def get_all_parameters(self) -> List[Parameter]:
        """Get flat list of all parameters across all blocks"""
        all_params = []
        for block in self.blocks.values():
            all_params.extend(block.parameters)
        return all_params

    def get_parameter_count(self) -> Dict[str, int]:
        """Get parameter count per block"""
        return {name: len(block.parameters) for name, block in self.blocks.items()}

    def print_summary(self):
        """Print a formatted summary of all tone blocks"""
        print("="*80)
        print("TONEX PRESET PARAMETER MODEL")
        print("="*80)
        print()

        counts = self.get_parameter_count()
        total = sum(counts.values())

        print(f"Total Parameters: {total}")
        print()

        for name, block in self.blocks.items():
            param_count = len(block.parameters)
            print(f"\n{'='*80}")
            print(f"{block.name.upper()} BLOCK ({param_count} parameters)")
            print(f"{'='*80}")
            print(f"{block.description}")
            print()

            for param in block.parameters:
                print(f"  {param.name}")
                print(f"    Type: {param.data_type.value}")
                print(f"    Desc: {param.description}")
                if param.value_range:
                    print(f"    Range: {param.value_range}")
                if param.notes:
                    print(f"    Notes: {param.notes}")
                print()

    def export_to_json(self) -> Dict[str, Any]:
        """Export model to JSON-compatible dictionary"""
        return {
            'model_name': 'ToneX Preset Parameter Model',
            'version': '1.0',
            'total_parameters': len(self.get_all_parameters()),
            'blocks': {
                name: block.get_param_dict()
                for name, block in self.blocks.items()
            }
        }


def main():
    """Main execution"""
    model = ToneXPresetModel()
    model.print_summary()

    print("\n" + "="*80)
    print("PARAMETER SUMMARY BY BLOCK")
    print("="*80)
    counts = model.get_parameter_count()
    for name, count in counts.items():
        print(f"  {name:20s}: {count:3d} parameters")
    print(f"  {'TOTAL':20s}: {sum(counts.values()):3d} parameters")
    print()


if __name__ == '__main__':
    main()
