import sys
import types
import traceback

# Let's see what happens if we mock spacy.pipeline.pipe and spacy.training.gold_io
def mock_mod(name):
    if name not in sys.modules:
        m = types.ModuleType(name)
        sys.modules[name] = m
        return m

mock_mod('spacy.pipeline.pipe')
mock_mod('spacy.training.gold_io')
mock_mod('spacy.vocab')
mock_mod('spacy.matcher._matcher')
mock_mod('spacy.tokens._retokenize')
mock_mod('spacy.morphology')
mock_mod('spacy.parts_of_speech')
mock_mod('spacy.syntax._parser')
mock_mod('spacy.syntax._state')
mock_mod('spacy.syntax.arc_eager')

try:
    import spacy
    print("spacy imported!")
except Exception as e:
    print("spacy failed:")
    traceback.print_exc()
