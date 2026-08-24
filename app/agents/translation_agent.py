from app.graph.state import DubbingState
from app.tools.translation_tools import translate_segments_to_marathi
from app.tools.genre_tools import detect_or_assign_genre
from app.tools.humor_tools import detect_humor_type
from app.tools.cultural_adaptation_tools import adapt_cultural_context

def run_translation_agent(state: DubbingState) -> DubbingState:
    print(f"Running Translation Agent for job {state['job_id']}")
    
    full_text = " ".join([s.get("text", "") for s in state['segments']])
    
    # Genre & Mood
    genre_res = detect_or_assign_genre(full_text, state.get('genre'))
    state['genre'] = genre_res['genre']
    state['scene_mood'] = genre_res['scene_mood']
    
    # Humor
    humor_res = detect_humor_type(full_text, state['genre'])
    state['humor_type'] = humor_res['humor_type']
    
    # Translate
    trans_res = translate_segments_to_marathi(state['segments'], {
        "genre": state['genre'],
        "scene_mood": state['scene_mood'],
        "speaker_map": state.get('speaker_map', {})
    })
    
    # Adapt and optimize syllable density for isochronous timestamp synchronization
    adapted = []
    for t in trans_res.get("translations", []):
        ad_res = adapt_cultural_context(t.get('original_text', ''), t['translated_text'], state['genre'], state['target_language'], original_text=t.get('original_text', ''))
        t['adapted_text'] = ad_res['adapted_translation']
        t['isochronous_ratio'] = ad_res.get('isochronous_ratio', 1.0)
        adapted.append(t)
        
    state['translations'] = adapted
    
    return state
