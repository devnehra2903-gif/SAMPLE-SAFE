# Sample-Safe

## Audio Copyright Risk Detection Tool for Musicians

Sample-Safe is a Python-based application designed to help musicians perform a preliminary check on audio recordings before using them in their own musical work.

The application uses audio-recognition services to identify whether an uploaded audio recording may match an existing published recording. It then displays information such as the possible track, artist, confidence level, and a preliminary copyright-risk classification.

> **Important:** Sample-Safe is a preliminary screening tool. It does not legally determine copyright ownership or whether a particular use of audio is permitted.

---

## 1. Problem Statement

Musicians may come across audio recordings that they want to use in their own musical work. However, it can be difficult to know whether the recording already exists in another published song or recording.

Using potentially copyrighted audio without proper verification can create problems for musicians later.

Sample-Safe aims to provide a simple first-level checking system that allows a musician to upload an audio file and determine whether the recording can be identified as an existing work.

---

## 2. Project Objective

The main objective of Sample-Safe is to provide musicians with a simple tool for preliminary audio verification.

The system aims to:

- Identify possible matches for an uploaded audio recording.
- Display the detected song and artist information.
- Compare recognition results from multiple audio-recognition services.
- Provide a confidence level for detected matches.
- Classify the result into a preliminary risk level.
- Maintain a history of previous scans.

---

## 3. Target Users

Sample-Safe is primarily intended for:

- Musicians
- Singers
- Songwriters
- Music producers
- Independent artists
- Content creators working with audio

The system can be useful whenever a user wants to perform a preliminary check on an audio recording before using it in their own work.

---

## 4. How Sample-Safe Works

The basic workflow of the application is:


        User
          │
          ▼
    Upload Audio File
          │
          ▼
      Sample-Safe
          │
          ├───────────────┐
          ▼               ▼
      AudD API       ACRCloud API
          │               │
          └───────┬───────┘
                  ▼
         Recognition Results
                  │
                  ▼
          Result Comparison
                  │
                  ▼
         Risk Classification
                  │
                  ▼
            Scan History