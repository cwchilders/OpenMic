#!/usr/bin/env python3
"""
Analyze ToneX Preset Parameters
Parses the schema and data dump to show which parameters are editable and their meanings
"""

import re
from typing import List, Dict, Tuple


def parse_schema(schema_line: str) -> List[str]:
    """Parse the schema definition to extract column names"""
    # Extract all column definitions between [ and ]
    columns = re.findall(r'\[([^\]]+)\]', schema_line)
    return columns


def parse_data_row(data_line: str) -> List[str]:
    """Parse a data row (tab-separated values)"""
    return data_line.strip().split('\t')


def categorize_parameters(columns: List[str]) -> Dict[str, List[str]]:
    """Categorize parameters by their function"""
    categories = {
        'Metadata': [],
        'Amp Model': [],
        'EQ': [],
        'Compression': [],
        'Noise Gate': [],
        'Modulation': [],
        'Delay': [],
        'Reverb': [],
        'Cabinet': [],
        'Hardware Control A': [],
        'Hardware Control B': [],
        'Other': []
    }

    for col in columns:
        if col.startswith('HWParamA_'):
            categories['Hardware Control A'].append(col)
        elif col.startswith('HWParamB_'):
            categories['Hardware Control B'].append(col)
        elif col in ['GUID', 'Version', 'ToneModel_GUID', 'OptionalToneModel_GUID', 'Tag_PresetName',
                     'Tag_UserName', 'Tag_ModelerTags', 'Tag_Date', 'Tag_ModelCategory', 'Tag_Instrument',
                     'Tag_InstrumentType', 'Tag_PickupPosition', 'Tag_PickupType', 'Tag_Artist',
                     'Tag_Album', 'Tag_Song', 'Tag_SongPart', 'Tag_Genre', 'Tag_Description']:
            categories['Metadata'].append(col)
        elif col.startswith('Eq') or col.startswith('PwrAmpEq'):
            categories['EQ'].append(col)
        elif col.startswith('Comp'):
            categories['Compression'].append(col)
        elif col.startswith('NoiseGate'):
            categories['Noise Gate'].append(col)
        elif col.startswith('Mod'):
            categories['Modulation'].append(col)
        elif col.startswith('Delay'):
            categories['Delay'].append(col)
        elif col.startswith('Reverb'):
            categories['Reverb'].append(col)
        elif col.startswith('Cab') or col.startswith('VIRCab'):
            categories['Cabinet'].append(col)
        elif col.startswith('Model') or col in ['BPM']:
            categories['Amp Model'].append(col)
        elif col in ['HW_ExtControllerEnable', 'Favorite']:
            categories['Other'].append(col)
        else:
            categories['Other'].append(col)

    return categories


def compare_presets(columns: List[str], preset1_data: List[str], preset2_data: List[str],
                   preset1_name: str, preset2_name: str) -> Dict[str, List[Tuple[str, str, str]]]:
    """Compare two presets and show differences"""
    differences = {}

    for i, col in enumerate(columns):
        if i < len(preset1_data) and i < len(preset2_data):
            val1 = preset1_data[i]
            val2 = preset2_data[i]

            if val1 != val2:
                # Skip GUID and similar unique identifiers
                if col not in ['GUID', 'ToneModel_GUID', 'OptionalToneModel_GUID', 'Tag_PresetName']:
                    category = None
                    if col.startswith('HWParam'):
                        continue  # Skip hardware params for now
                    elif col.startswith('Eq') or col.startswith('PwrAmpEq'):
                        category = 'EQ'
                    elif col.startswith('Mod'):
                        category = 'Modulation'
                    elif col.startswith('Delay'):
                        category = 'Delay'
                    elif col.startswith('Reverb'):
                        category = 'Reverb'
                    elif col.startswith('Model'):
                        category = 'Amp Model'
                    elif col.startswith('Comp'):
                        category = 'Compression'
                    elif col.startswith('NoiseGate'):
                        category = 'Noise Gate'
                    elif col.startswith('Cab') or col.startswith('VIRCab'):
                        category = 'Cabinet'
                    else:
                        category = 'Other'

                    if category not in differences:
                        differences[category] = []
                    differences[category].append((col, val1, val2))

    return differences


def display_preset_params(columns: List[str], data: List[str], preset_name: str):
    """Display key parameters for a preset"""
    param_map = dict(zip(columns, data))

    print(f"\n{'='*80}")
    print(f"PRESET: {preset_name}")
    print(f"{'='*80}")

    # Metadata
    print("\n## METADATA")
    print(f"  Category: {param_map.get('Tag_ModelCategory', 'N/A')}")
    print(f"  Genre: {param_map.get('Tag_Genre', 'N/A')}")
    print(f"  Description: {param_map.get('Tag_Description', 'N/A')}")

    # Amp Model Settings
    print("\n## AMP MODEL SETTINGS (Main tone controls)")
    print(f"  ModelEnable: {param_map.get('ModelEnable', 'N/A')} (1=on, 0=off)")
    print(f"  ModelMix: {param_map.get('ModelMix', 'N/A')}% (wet/dry blend)")
    print(f"  ModelGain: {param_map.get('ModelGain', 'N/A')} (input gain/drive)")
    print(f"  ModelVolume: {param_map.get('ModelVolume', 'N/A')} (output level)")
    print(f"  PwrAmpEqPresence: {param_map.get('PwrAmpEqPresence', 'N/A')} (high-end clarity)")
    print(f"  PwrAmpEqDepth: {param_map.get('PwrAmpEqDepth', 'N/A')} (low-end resonance)")

    # EQ
    print("\n## EQ (Tone shaping)")
    print(f"  EqPost: {param_map.get('EqPost', 'N/A')} (0=pre-amp, 1=post-amp)")
    print(f"  EqBass: {param_map.get('EqBass', 'N/A')} @ {param_map.get('EqBassFreq', 'N/A')} Hz")
    print(f"  EqMid: {param_map.get('EqMid', 'N/A')} @ {param_map.get('EqMidFreq', 'N/A')} Hz (Q: {param_map.get('EqMidQ', 'N/A')})")
    print(f"  EqTreble: {param_map.get('EqTreble', 'N/A')} @ {param_map.get('EqTrebleFreq', 'N/A')} Hz")

    # Compression
    print("\n## COMPRESSION")
    print(f"  CompEnable: {param_map.get('CompEnable', 'N/A')}")
    print(f"  CompThreshold: {param_map.get('CompThreshold', 'N/A')} dB")
    print(f"  CompMakeUp: {param_map.get('CompMakeUp', 'N/A')} dB")
    print(f"  CompAttack: {param_map.get('CompAttack', 'N/A')} ms")

    # Noise Gate
    print("\n## NOISE GATE")
    print(f"  NoiseGateEnable: {param_map.get('NoiseGateEnable', 'N/A')}")
    print(f"  NoiseGateThreshold: {param_map.get('NoiseGateThreshold', 'N/A')} dB")
    print(f"  NoiseGateRelease: {param_map.get('NoiseGateRelease', 'N/A')} ms")
    print(f"  NoiseGateDepth: {param_map.get('NoiseGateDepth', 'N/A')} dB")

    # Modulation
    print("\n## MODULATION")
    print(f"  ModEnable: {param_map.get('ModEnable', 'N/A')}")
    print(f"  ModModel: {param_map.get('ModModel', 'N/A')} (0=chorus, 1=tremolo, 2=phaser, 3=flanger, 4=rotary)")
    if param_map.get('ModModel') == '0':  # Chorus
        print(f"  Chorus Rate: {param_map.get('ModChorusRate', 'N/A')}")
        print(f"  Chorus Depth: {param_map.get('ModChorusDepth', 'N/A')}")
        print(f"  Chorus Level: {param_map.get('ModChorusLevel', 'N/A')}")

    # Delay
    print("\n## DELAY")
    print(f"  DelayEnable: {param_map.get('DelayEnable', 'N/A')}")
    print(f"  DelayModel: {param_map.get('DelayModel', 'N/A')} (0=digital, 1=tape)")
    print(f"  DelayDigitalTime: {param_map.get('DelayDigitalTime', 'N/A')} ms")
    print(f"  DelayDigitalFeedback: {param_map.get('DelayDigitalFeedback', 'N/A')}%")
    print(f"  DelayDigitalMix: {param_map.get('DelayDigitalMix', 'N/A')}%")

    # Reverb
    print("\n## REVERB")
    print(f"  ReverbEnable: {param_map.get('ReverbEnable', 'N/A')}")
    print(f"  ReverbModel: {param_map.get('ReverbModel', 'N/A')} (4=spring, 5=room, 6=plate)")
    print(f"  ReverbPosition: {param_map.get('ReverbPosition', 'N/A')} (0=pre, 1=post)")

    # Cabinet
    print("\n## CABINET")
    print(f"  CabType: {param_map.get('CabType', 'N/A')} (0=VIR, 2=classic)")
    print(f"  VIRCabModel: {param_map.get('VIRCabModel', 'N/A')}")
    print(f"  VIRCabMic1Model: {param_map.get('VIRCabMic1Model', 'N/A')}")
    print(f"  VIRCabMicBlend: {param_map.get('VIRCabMicBlend', 'N/A')}")


def main():
    schema_file = 'schema_library_Presets.lst'
    data_file = 'z_maz18_dump_sqlLite.txt'

    # Read schema
    with open(schema_file, 'r') as f:
        schema_line = f.read().strip()

    columns = parse_schema(schema_line)
    print(f"Found {len(columns)} columns in schema")

    # Categorize parameters
    categories = categorize_parameters(columns)

    print("\n" + "="*80)
    print("PARAMETER CATEGORIES")
    print("="*80)

    # Show non-HW parameters
    for cat_name in ['Metadata', 'Amp Model', 'EQ', 'Compression', 'Noise Gate',
                     'Modulation', 'Delay', 'Reverb', 'Cabinet', 'Other']:
        params = categories[cat_name]
        if params:
            print(f"\n{cat_name} ({len(params)} params):")
            for param in params[:10]:  # Show first 10
                print(f"  - {param}")
            if len(params) > 10:
                print(f"  ... and {len(params) - 10} more")

    print(f"\nHardware Control A: {len(categories['Hardware Control A'])} params (HWParamA_*)")
    print(f"Hardware Control B: {len(categories['Hardware Control B'])} params (HWParamB_*)")

    # Read data
    print("\n" + "="*80)
    print("READING PRESET DATA")
    print("="*80)

    with open(data_file, 'r') as f:
        data_lines = [line for line in f.readlines() if line.strip()]

    presets = []
    for line in data_lines:
        data = parse_data_row(line)
        if len(data) >= 5:  # At least has preset name
            preset_name = data[4] if len(data) > 4 else 'Unknown'
            presets.append((preset_name, data))

    print(f"Found {len(presets)} presets")

    # Display first preset in detail
    if presets:
        display_preset_params(columns, presets[0][1], presets[0][0])

    # Compare two presets
    if len(presets) >= 2:
        print("\n" + "="*80)
        print(f"COMPARING: {presets[1][0]} vs {presets[2][0]}")
        print("="*80)

        diffs = compare_presets(columns, presets[1][1], presets[2][1],
                               presets[1][0], presets[2][0])

        for category, changes in sorted(diffs.items()):
            if changes:
                print(f"\n{category}:")
                for param, val1, val2 in changes[:10]:
                    print(f"  {param}: {val1} → {val2}")
                if len(changes) > 10:
                    print(f"  ... and {len(changes) - 10} more differences")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY: EDITABLE PARAMETERS")
    print("="*80)
    print("""
The HWParam parameters (HWParamA_* and HWParamB_*) are likely for hardware control
mapping (e.g., mapping physical knobs/pedals to parameters). You're correct that
these are probably not relevant for basic preset editing.

For editing ToneX presets, focus on these parameter groups:

1. **Amp Model** - Core tone (ModelGain, ModelVolume, PwrAmpEq*)
2. **EQ** - Tone shaping (EqBass, EqMid, EqTreble + frequencies)
3. **Effects** - Modulation, Delay, Reverb (enable/disable + settings)
4. **Cabinet** - Speaker simulation (CabType, VIRCab*)
5. **Dynamics** - Compression and Noise Gate

The Tag_* fields are metadata (artist, genre, etc.) for organization.
    """)


if __name__ == '__main__':
    main()
