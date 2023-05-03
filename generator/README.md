# Generator

Generators to combine automatically all shapes, ontologies, etc.
from the different modules into a single resource to allow
using a single prefix for all modules.

- `generate-ontology.py`: Combines the ontologies of all modules into a single ontology file: `../ontology.ttl`
- `generate-shapes.py`: Combines the SHACL shapes of all modules into a single SHACL shape file: `../shapes.ttl`
- `generate-backwards-compatibility.py`: Combines the backwards compatibility descriptions into a single file: `../backwards-compatible.ttl`
