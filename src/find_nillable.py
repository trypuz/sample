# Licensed under the Apache License, Version 2.0 (the "License");
# pyou may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oblib import taxonomy

tax = taxonomy.Taxonomy()

false_count = 0
true_count = 0

print()
print("Nillable fields List:")
print("=====================")

for key, e in tax.semantic.get_all_concepts(details=True).items():
    if not e.nillable:
        print(e.name)
        false_count += 1
    else:
        true_count += 1

print()
print("Number of True values found: ", true_count)
print("Number of False values found: ", false_count)
print()
