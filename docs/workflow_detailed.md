# NATURALDUB-AI: Detailed Workflow Architecture (Steps 3 to 8)

This document provides a comprehensive architectural and technical breakdown of **Steps 3 through 8** of the **NATURALDUB-AI** pipeline. It outlines the exact machine learning models, signal processing algorithms, LangGraph state transitions, and backend tool interactions powering each stage.

---

## 🏗️ Workflow Overview (Steps 3 to 8)

```mermaid
graph TD
    classDef agent fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#fff;
    classDef gate fill:#7c2d12,stroke:#f97316,stroke-width:2px,color:#fff;
    classDef tool fill:#0f172a,stroke:#64748b,stroke-width:1px,color:#cbd5e1;

    A1["🤖 Step 3: Agent 1 (Media Understanding)"] ::: agent
    G1["🛑 Step 4: Human Review Gate 1"] ::: gate
    A2["🤖 Step 5: Agent 2 (Translation & Culture)"] ::: agent
    G2["🛑 Step 6: Human Review Gate 2"] ::: gate
    A3["🤖 Step 7: Agent 3 (Voice & Emotion)"] ::: agent
    A4["🤖 Step 8: Agent 4 (Sync, Mixing & QA)"] ::: agent

    A1 -->|"Extracts & Slices Audio"| G1
    G1 -->|"POST /api/review/transcript"| A2
    A2 -->|"Isochronous Text Adaptation"| G2
    G2 -->|"POST /api/review/translation"| A3
    A3 -->|"Zero-Shot Vocal Cloning"| A4
    A4 -->|"19 QA Metrics & Final MP4"| Done(["🏁 Completed Video"])

    subgraph Tools_A1 [Agent 1 Tools]
        T1[ffmpeg_tools.py] ::: tool
        T2[separation_tools.py] ::: tool
        T3[transcription_tools.py] ::: tool
        T4[diarization_tools.py] ::: tool
    end
    A1 -.- Tools_A1

    subgraph Tools_A2 [Agent 2 Tools]
        T5[genre_tools.py / humor_tools.py] ::: tool
        T6[translation_tools.py] ::: tool
        T7[cultural_adaptation_tools.py] ::: tool
    end
    A2 -.- Tools_A2

    subgraph Tools_A3 [Agent 3 Tools]
        T8[consent_service.py] ::: tool
        T9[xtts_cloning_tools.py] ::: tool
        T10[synthesis_tools.py Cascade] ::: tool
    end
    A3 -.- Tools_A3

    subgraph Tools_A4 [Agent 4 Tools]
        T11[alignment_tools.py] ::: tool
        T12[mixing_tools.py] ::: tool
        T13[lipsync_tools.py] ::: tool
        T14[evaluation_tools.py] ::: tool
    end
    A4 -.- Tools_A4
```

---

## 3. 🤖 Agent 1 (Media Understanding)
**Implementation**: [`app/agents/media_agent.py`](../app/agents/media_agent.py)

This agent acts as the ingestion and acoustic analysis engine. It breaks down raw video containers into isolated acoustic components and generates synchronized linguistic timestamps.

### **Detailed Tool Breakdown:**
1. **Audio Extraction ([`ffmpeg_tools.py`](../app/tools/ffmpeg_tools.py))**:
   - Invokes underlying FFmpeg C-binaries to demux the video container (`.mp4`/`.mkv`).
   - Converts multi-channel, compressed audio streams into **16kHz mono uncompressed PCM WAV** (`raw_audio.wav`), which is the exact acoustic input format required by Whisper and Pyannote neural networks.
2. **Audio Source Separation ([`separation_tools.py`](../app/tools/separation_tools.py))**:
   - Runs **Meta Demucs (HTDemucs)** deep neural network to perform stem separation.
   - Splits the waveform into two clean audio tracks:
     - `vocals.wav`: Contains 100% isolated human dialogue (stripped of background noise).
     - `background.wav`: Contains ambient sound effects (SFX), explosions, footsteps, and background music (saved for Step 8 mixing).
3. **Speech-to-Text Transcription ([`transcription_tools.py`](../app/tools/transcription_tools.py))**:
   - Feeds `vocals.wav` into **Faster-Whisper (CTranslate2 optimized)**.
   - Generates transcribed text segments along with **word-level timestamps** ($t_{start}, t_{end}$ in seconds with millisecond precision).
4. **Speaker Diarization & Reference Extraction ([`diarization_tools.py`](../app/tools/diarization_tools.py))**:
   - Uses **Pyannote Audio** (speaker clustering & embedding network) to answer *"who spoke when?"*.
   - Assigns temporary speaker IDs (e.g., `SPEAKER_00`, `SPEAKER_01`) to each transcribed segment.
   - **Reference Audio Slicing**: Automatically slices and exports clean 5–15 second audio samples of each detected speaker (`ref_001.wav`, `ref_002.wav`) from `vocals.wav`. These files serve as the ground-truth acoustic references for zero-shot voice cloning in Step 7.

> [!TIP]
> **Why Demucs before Whisper?** Feeding raw movie audio directly into Whisper causes hallucinations and transcription errors due to background music and sound effects. Isolating `vocals.wav` first dramatically increases Whisper's Word Error Rate (WER) accuracy.

---

## 4. 🛑 Human Review Gate 1 (Transcript & Speaker Verification)
**Implementation**: [`app/api/routes_review.py`](../app/api/routes_review.py) | **UI View**: `ui/pages/2_Transcript_Review.py`

In an automated AI pipeline, transcription typos or misattributed speaker tags propagate downstream, ruining the final dubbed video. This gate introduces an explicit **Human-In-The-Loop (HITL)** checkpoint.

### **How It Works:**
1. **LangGraph Interruption**: When Agent 1 finishes, the LangGraph state machine hits an explicit breakpoint (`interrupt_before=['review_transcript']`). The job status in SQLite updates to `review_transcript`, and execution is frozen.
2. **Interactive UI Verification**:
   - The user opens the Streamlit review dashboard and listens to individual audio snippets while reading the text.
   - **Corrections**: The user fixes ASR spelling errors, adjusts timestamp boundaries if speech overlaps occurred, and renames generic speaker IDs to real actor names (e.g., mapping `"SPEAKER_00"` $\rightarrow$ `"Raj"` and `"SPEAKER_01"` $\rightarrow$ `"Simran"`).
3. **Workflow Resumption**:
   - When the user clicks **"Approve Transcript"**, the frontend sends a payload via `POST /api/review/transcript`.
   - The backend updates the SQLite database with the human-verified segments and calls `graph.invoke(None, config)` to deterministically resume the state machine from where it paused.

---

## 5. 🤖 Agent 2 (Translation & Cultural Adaptation)
**Implementation**: [`app/agents/translation_agent.py`](../app/agents/translation_agent.py)

This agent transforms English dialogue into the target regional language (e.g., Hindi, Marathi, Tamil) while preserving emotional context and ensuring visual lip-sync pacing.

### **Detailed Tool Breakdown:**
1. **Genre & Humor Analysis ([`genre_tools.py`](../app/tools/genre_tools.py), [`humor_tools.py`](../app/tools/humor_tools.py))**:
   - Analyzes dialogue context to classify tone (e.g., *sarcastic, dramatic, comedic, formal*).
   - Identifies idioms and cultural references that cannot be translated literally, tagging them for localized substitution.
2. **Neural Machine Translation ([`translation_tools.py`](../app/tools/translation_tools.py))**:
   - Translates text using **AI4Bharat IndicTrans2** (or structured LLM translation prompts with strict JSON parsing to prevent extra chat commentary).
3. **Isochronous Syllable Density Adaptation ([`cultural_adaptation_tools.py`](../app/tools/cultural_adaptation_tools.py))**:
   - **The Pacing Problem**: Indian languages often require more syllables than English to express the same thought. If a translation is too long, the TTS engine will speak at an unnaturally rapid, chipmunk-like speed to fit the timestamp window.
   - **The Mathematical Engine**: Computes the syllable/word density ratio $R$:
     $$R = \frac{\text{Word Count}_{\text{Translated}}}{\text{Word Count}_{\text{Original}}}$$
   - **Automated Rules**:
     - **If $R > 1.35$ (Too Verbose)**: Applies regex pruning rules to drop redundant auxiliary verb endings or polite suffixes while preserving core semantic meaning (condensing text).
     - **If $R < 0.65$ (Too Terse)**: Injects natural linguistic filler words or emphasis particles to pad the sentence duration (expanding text).

---

## 6. 🛑 Human Review Gate 2 (Translation Verification)
**Implementation**: [`app/api/routes_review.py`](../app/api/routes_review.py) | **UI View**: `ui/pages/3_Translation_Review.py`

This gate ensures cultural authenticity and gives the user absolute control over the final script before intensive GPU voice cloning begins.

### **How It Works:**
1. **LangGraph Interruption**: Workflow execution halts automatically (`interrupt_before=['review_translation']`), setting job status to `review_translation`.
2. **Interactive UI Verification**:
   - The user reviews a side-by-side comparison table showing: **Original English Text** | **Literal Translation** | **Adapted Isochronous Text** | **Timestamp Duration**.
   - The user can edit phrasing, rewrite slang, or shorten sentences if they anticipate lip-sync timing issues.
3. **Workflow Resumption**:
   - Clicking **"Approve Translation"** triggers `POST /api/review/translation`.
   - The verified Marathi/Hindi script is locked into the SQLite database, and the graph resumes to trigger voice synthesis.

---

## 7. 🤖 Agent 3 (Voice & Emotion Synthesis)
**Implementation**: [`app/agents/voice_emotion_agent.py`](../app/agents/voice_emotion_agent.py)

This agent generates neural speech in the target language while replicating the exact vocal timbre, pitch, and emotional cadence of the original actors.

### **Detailed Tool Breakdown:**
1. **Ethical AI Consent Guard ([`consent_service.py`](../app/services/consent_service.py))**:
   - Checks database flags (`consent_verified`). If voice cloning consent is missing or flagged as unauthorized, execution is blocked immediately to prevent ethical misuse or deepfake generation.
2. **Zero-Shot Vocal Timbre Cloning ([`xtts_cloning_tools.py`](../app/tools/xtts_cloning_tools.py))**:
   - Uses **Coqui XTTS-v2** (a flow-matching autoregressive transformer vocoder).
   - **How Zero-Shot Works**: Takes the adapted Marathi text and feeds it alongside the actor's clean reference audio (`ref_001.wav` extracted in Step 3). The acoustic encoder extracts a **512-dimensional speaker embedding vector ($e_s$)** representing the actor's vocal tract geometry and pitch. It generates new Marathi speech matching that exact voice—**without any gradient backpropagation or model fine-tuning**.
   - *Why frequency shifting is disabled here*: Because XTTS-v2 natively conditions on $e_s$, applying artificial post-processing frequency shifts (`match_voice_frequency`) would distort the formants and ruin natural audio quality.
3. **4-Tier Prioritized Fallback Cascade ([`synthesis_tools.py`](../app/tools/synthesis_tools.py))**:
   - To guarantee fault tolerance against GPU out-of-memory (OOM) crashes or network disconnects, the agent implements a defensive cascade:

| Fallback Tier | Model / Service | Why Used / When Triggered |
| :--- | :--- | :--- |
| **Tier 1 (Primary)** | **ElevenLabs IVC API** | Highest cloud quality voice cloning; used if API keys and credits are available. |
| **Tier 2 (Local ML)** | **Coqui XTTS-v2** | Local zero-shot cloning on local GPU VRAM; triggered if cloud APIs fail or are offline. |
| **Tier 3 (Regional)** | **AI4Bharat IndicF5** | Specialized Indian language TTS; triggered if XTTS fails on specific complex Indic phonemes. |
| **Tier 4 (Fallback)** | **Kokoro / Azure TTS** | High-reliability parametric TTS; triggered if GPU memory is completely exhausted. *(Note: Librosa artificial frequency shifting is applied here to match median actor pitch).* |

---

## 8. 🤖 Agent 4 (Sync, Mixing & QA Evaluation)
**Implementation**: [`app/agents/sync_qa_agent.py`](../app/agents/sync_qa_agent.py)

The final assembly engine. It perfectly synchronizes audio durations, remixes background music, animates video lip movements, and computes mathematical quality metrics.

### **Detailed Tool Breakdown:**
1. **Mathematical Audio Time-Stretching ([`alignment_tools.py`](../app/tools/alignment_tools.py))**:
   - Compares generated speech duration ($T_{actual}$) against the visual timestamp window ($T_{target} = t_{end} - t_{start}$).
   - If there is a mismatch (e.g., audio is 4.2s but visual window is 3.8s), it calculates the scaling ratio $\alpha = \frac{T_{actual}}{T_{target}}$.
   - Uses **Pydub / SOLA (Synchronized Overlap-Add)** algorithms to time-stretch or compress the audio waveform while **preserving the fundamental frequency ($F_0$)**, ensuring speech fits the exact video frames without pitch distortion.
2. **Audio Mixing & Multiplexing ([`mixing_tools.py`](../app/tools/mixing_tools.py))**:
   - Takes the time-aligned Marathi dialogue tracks and overlays them onto the original clean background music/SFX track (`background.wav` from Step 3).
   - Applies audio ducking (lowering music volume slightly during speech) and merges the audio streams into a mastered stereo track.
3. **Visual Lip-Sync Generation ([`lipsync_tools.py`](../app/tools/lipsync_tools.py))**:
   - Feeds the original video frames and the newly mastered Marathi audio into **Wav2Lip** (a GAN-based visual phoneme-to-lip warping network).
   - Dynamically modifies the lower-half facial pixels of the actors in the video so their lip movements match the spoken Marathi syllables.
4. **Automated QA Evaluation ([`evaluation_tools.py`](../app/tools/evaluation_tools.py))**:
   - Computes **19 objective quality metrics** across audio clarity, synchronization, and translation accuracy, exporting a detailed `evaluation_report.json`. Key metrics include:
     - **Signal-to-Noise Ratio (SNR)** & **Total Harmonic Distortion (THD)** for audio clarity.
     - **Lip-Sync Cross-Correlation Score** measuring audio-visual timestamp alignment.
     - **BLEU / chrF++ scores** verifying translation fidelity against ground truth.
   - Updates job status to `completed`. The user can view the final dubbed video, inspect spectrograms, and download reports on UI Page 6 (`6_Final_Evaluation.py`).

---

## 💡 Key Architectural Takeaways
* **Why LangGraph over Celery/LangChain?** While Celery distributes blind background tasks, LangGraph maintains a stateful cyclic graph (`DubbingState`) with native `interrupt_before` breakpoints, making seamless REST API human-in-the-loop verification possible without losing GPU context or database synchronization.
* **Why Demucs + SOLA + XTTS?** Combining acoustic separation (Demucs), zero-shot embedding cloning (XTTS-v2), and pitch-preserving time-stretching (SOLA) allows NATURALDUB-AI to produce studio-grade regional movie dubbing entirely on local workstation hardware.
