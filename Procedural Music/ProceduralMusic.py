# Python code to generate procedural music and play the generated MIDI file

import random
import midiutil
from midiutil.MidiFile import MIDIFile

# Create a dictionary of scales, notes and relative keys: {scale: "C Major", notes: ["C", "D", "E", "F", "G", "A", "B"], relative_keys: ["A Minor", "D Dorian", "E Phrygian", "F Lydian", "G Mixolydian", "B Locrian"]}
scales = {
    "C Major": {"notes": ["C", "D", "E", "F", "G", "A", "B"], "relative_keys": ["A Minor", "D Dorian", "E Phrygian", "F Lydian", "G Mixolydian", "B Locrian"]},
    "A Minor": {"notes": ["A", "B", "C", "D", "E", "F", "G"], "relative_keys": ["C Major", "D Dorian", "E Phrygian", "F Lydian", "G Mixolydian", "B Locrian"]},
    "D Dorian": {"notes": ["D", "E", "F", "G", "A", "B", "C"], "relative_keys": ["C Major", "A Minor", "E Phrygian", "F Lydian", "G Mixolydian", "B Locrian"]},
    "E Phrygian": {"notes": ["E", "F", "G", "A", "B", "C", "D"], "relative_keys": ["C Major", "A Minor", "D Dorian", "F Lydian", "G Mixolydian", "B Locrian"]},
    "F Lydian": {"notes": ["F", "G", "A", "B", "C", "D", "E"], "relative_keys": ["C Major", "A Minor", "D Dorian", "E Phrygian", "G Mixolydian", "B Locrian"]},
    "G Mixolydian": {"notes": ["G", "A", "B", "C", "D", "E", "F"], "relative_keys": ["C Major", "A Minor", "D Dorian", "E Phrygian", "F Lydian", "B Locrian"]},
    "B Locrian": {"notes": ["B", "C", "D", "E", "F", "G", "A"], "relative_keys": ["C Major", "A Minor", "D Dorian", "E Phrygian", "F Lydian", "G Mixolydian"]}
}

# Create a dictionary of chords: {chord: "Major", notes: [0, 4, 7], relative_chords: ["Minor", "Diminished", "Augmented"]}
chords = {
    "Major": {"notes": [0, 4, 7], "relative_chords": ["Minor", "Diminished", "Augmented"]},
    "Minor": {"notes": [0, 3, 7], "relative_chords": ["Major", "Diminished", "Augmented"]},
    "Diminished": {"notes": [0, 3, 6], "relative_chords": ["Major", "Minor", "Augmented"]},
    "Augmented": {"notes": [0, 4, 8], "relative_chords": ["Major", "Minor", "Diminished"]}
}

# Create a dictionary of chord progressions: {progression: "I-IV-V", chords: ["I", "IV", "V"], relative_progressions: ["I-V-IV", "IV-V-I", "IV-I-V", "V-I-IV", "V-IV-I"]}
progressions = {
    "I-IV-V": {"chords": ["I", "IV", "V"], "relative_progressions": ["I-V-IV", "IV-V-I", "IV-I-V", "V-I-IV", "V-IV-I"]},
    "I-V-IV": {"chords": ["I", "V", "IV"], "relative_progressions": ["I-IV-V", "IV-V-I", "IV-I-V", "V-I-IV", "V-IV-I"]},
    "IV-V-I": {"chords": ["IV", "V", "I"], "relative_progressions": ["I-IV-V", "I-V-IV", "IV-I-V", "V-I-IV", "V-IV-I"]},
    "IV-I-V": {"chords": ["IV", "I", "V"], "relative_progressions": ["I-IV-V", "I-V-IV", "IV-V-I", "V-I-IV", "V-IV-I"]},
    "V-I-IV": {"chords": ["V", "I", "IV"], "relative_progressions": ["I-IV-V", "I-V-IV", "IV-V-I", "IV-I-V", "V-IV-I"]},
    "V-IV-I": {"chords": ["V", "IV", "I"], "relative_progressions": ["I-IV-V", "I-V-IV", "IV-V-I", "IV-I-V", "V-I-IV"]}
}

# Create a dictionary of rhythms: {rhythm: "4/4", beats: 4, relative_rhythms: ["3/4", "5/4", "6/8", "7/8", "9/8", "12/8"]}
rhythms = {
    "4/4": {"beats": 4, "relative_rhythms": ["3/4", "5/4", "6/8", "7/8", "9/8", "12/8"]},
    "3/4": {"beats": 3, "relative_rhythms": ["4/4", "5/4", "6/8", "7/8", "9/8", "12/8"]},
    "5/4": {"beats": 5, "relative_rhythms": ["3/4", "4/4", "6/8", "7/8", "9/8", "12/8"]},
    "6/8": {"beats": 6, "relative_rhythms": ["3/4", "4/4", "5/4", "7/8", "9/8", "12/8"]},
    "7/8": {"beats": 7, "relative_rhythms": ["3/4", "4/4", "5/4", "6/8", "9/8", "12/8"]},
    "9/8": {"beats": 9, "relative_rhythms": ["3/4", "4/4", "5/4", "6/8", "7/8", "12/8"]},
    "12/8": {"beats": 12, "relative_rhythms": ["3/4", "4/4", "5/4", "6/8", "7/8", "9/8"]}
}

# Create a dictionary of instruments: {instrument: "Piano", family: "Keyboard", relative_instruments: ["Organ", "Harpsichord", "Clavichord", "Celesta", "Accordion", "Harmonica"]}
instruments = {
    "Piano": {"family": "Keyboard", "relative_instruments": ["Organ", "Harpsichord", "Clavichord", "Celesta", "Accordion", "Harmonica"]},
    "Organ": {"family": "Keyboard", "relative_instruments": ["Piano", "Harpsichord", "Clavichord", "Celesta", "Accordion", "Harmonica"]},
    "Harpsichord": {"family": "Keyboard", "relative_instruments": ["Piano", "Organ", "Clavichord", "Celesta", "Accordion", "Harmonica"]},
    "Clavichord": {"family": "Keyboard", "relative_instruments": ["Piano", "Organ", "Harpsichord", "Celesta", "Accordion", "Harmonica"]},
    "Celesta": {"family": "Keyboard", "relative_instruments": ["Piano", "Organ", "Harpsichord", "Clavichord", "Accordion", "Harmonica"]},
    "Accordion": {"family": "Keyboard", "relative_instruments": ["Piano", "Organ", "Harpsichord", "Clavichord", "Celesta", "Harmonica"]},
    "Harmonica": {"family": "Keyboard", "relative_instruments": ["Piano", "Organ", "Harpsichord", "Clavichord", "Celesta", "Accordion"]}
}

# Function to generate a random scale from the previously played scale's relative keys
# (if there is no previously played scale, generate a random scale from the scales dictionary)
def generate_scale(current_scale=None):
    if current_scale:
        relative_keys = scales[current_scale]["relative_keys"]
        scale = random.choice(relative_keys)
    else:
        scale = random.choice(list(scales.keys()))
    current_scale = scale
    return scale

# Function to convert the notes of a scale to MIDI note numbers
def scale_to_midi(scale):
    notes = scales[scale]["notes"]
    midi_notes = []
    for note in notes:
        midi_note = 60 + notes.index(note)
        midi_notes.append(midi_note)
    return midi_notes

# Function to generate a random chord progression from the previously played progression's relative progressions
# (if there is no previously played progression, generate a random progression from the progressions dictionary)
def generate_progression(current_progression=None):
    if current_progression:
        relative_progressions = progressions[current_progression]["relative_progressions"]
        progression = random.choice(relative_progressions)
    else:
        progression = random.choice(list(progressions.keys()))
    current_progression = progression
    return progression

# Choose a random scale
current_scale = generate_scale()
print("Current scale:", current_scale)

# Choose a random rhythm
current_rhythm = random.choice(list(rhythms.keys()))
print("Current rhythm:", current_rhythm)

# Choose a random tempo
tempo = random.randint(60, 180)

# Choose a random instrument
current_instrument = random.choice(list(instruments.keys()))
print("Current instrument:", current_instrument)

# Create the MIDIFile Object
MyMIDI = MIDIFile(1)

# Add track name and tempo
track = 0
time = 0
MyMIDI.addTrackName(track, time, "Sample Track")
MyMIDI.addTempo(track, time, tempo)

# Add program change
channel = 0
program = 0
MyMIDI.addProgramChange(track, channel, time, program)

for bar in range(4):
    # Choose 8 random notes from the current scale
    scale_notes = scale_to_midi(current_scale)
    notes = random.choices(scale_notes, k=8)
    print("Notes:", notes)

    # Add the notes to the MIDI file
    for note in notes:
        MyMIDI.addNote(track, channel, note, time, 4, random.randint(50, 100))
        time += 1

    # Choose a random scale
    current_scale = generate_scale(current_scale)
    print("Current scale:", current_scale)

# And write it to disk.
binfile = open("output.mid", 'wb')
MyMIDI.writeFile(binfile)
binfile.close()

# Play the generated MIDI file
import pygame
pygame.init()
pygame.mixer.music.load("output.mid")

pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
    pygame.time.wait(1000)
    print("Playing...")
print("Done playing!")
pygame.quit()