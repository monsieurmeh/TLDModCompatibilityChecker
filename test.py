import re

def extract_harmony_patches_from_code(code):
    matches = []

    def normalize(cls, method):
        if not cls:
            cls = '?UnknownClass'
        if not method:
            return cls

        cls_parts = cls.split('.')
        method_parts = method.split('.')

        # Find largest k where last k parts of class == first k parts of method
        max_overlap = 0
        max_k = min(len(cls_parts), len(method_parts))
        for k in range(max_k, 0, -1):
            if cls_parts[-k:] == method_parts[:k]:
                max_overlap = k
                break

        method_suffix = method_parts[max_overlap:] if max_overlap else method_parts

        return f"{cls}.{'.'.join(method_suffix)}"

    # 1. [HarmonyPatch("Class.Method")]
    matches += [
        normalize(*full.rsplit('.', 1))
        for full in re.findall(
            r'\[HarmonyPatch\s*\(\s*"([\w\.]+\.[\w]+)"\s*(?:,\s*new\s+Type\[\]\s*\{[^\}]*\})?\s*\)\]',
            code
        )
    ]

    # 2. [HarmonyPatch("Class", "Method")]
    matches += [
        normalize(cls, method)
        for cls, method in re.findall(
            r'\[HarmonyPatch\s*\(\s*"([\w\.]+)"\s*,\s*"([\w\.]+)"\s*(?:,\s*new\s+Type\[\]\s*\{[^\}]*\})?\s*\)\]',
            code
        )
    ]

    # 3. [HarmonyPatch("Class", nameof(Method))]
    matches += [
        normalize(cls, method)
        for cls, method in re.findall(
            r'\[HarmonyPatch\s*\(\s*"([\w\.]+)"\s*,\s*nameof\s*\(\s*([\w\.]+)\s*\)\s*(?:,\s*new\s+Type\[\]\s*\{[^\}]*\})?\s*\)\]',
            code
        )
    ]

    # 4. [HarmonyPatch(nameof(Class.Method))]
    matches += [
        normalize(*full.rsplit('.', 1))
        for full in re.findall(
            r'\[HarmonyPatch\s*\(\s*nameof\s*\(\s*([\w\.]+\.[\w]+)\s*\)\s*(?:,\s*new\s+Type\[\]\s*\{[^\}]*\})?\s*\)\]',
            code
        )
    ]

    # 5. [HarmonyPatch(nameof(Class), "Method")]
    matches += [
        normalize(cls, method)
        for cls, method in re.findall(
            r'\[HarmonyPatch\s*\(\s*nameof\s*\(\s*([\w\.]+)\s*\)\s*,\s*"([\w\.]+)"\s*(?:,\s*new\s+Type\[\]\s*\{[^\}]*\})?\s*\)\]',
            code
        )
    ]

    # 6. [HarmonyPatch(nameof(Class), nameof(Method))]
    matches += [
        normalize(cls, method)
        for cls, method in re.findall(
            r'\[HarmonyPatch\s*\(\s*nameof\s*\(\s*([\w\.]+)\s*\)\s*,\s*nameof\s*\(\s*([\w\.]+)\s*\)\s*(?:,\s*new\s+Type\[\]\s*\{[^\}]*\})?\s*\)\]',
            code
        )
    ]

    # 7. [HarmonyPatch(typeof(Class))]
    matches += [
        normalize(*cls.rsplit('.', 1)) if '.' in cls else normalize(cls, None)
        for cls in re.findall(
            r'\[HarmonyPatch\s*\(\s*typeof\s*\(\s*([\w\.]+)\s*\)\s*(?:,\s*new\s+Type\[\]\s*\{[^\}]*\})?\s*\)\]',
            code
        )
    ]

    # 8. [HarmonyPatch(typeof(Class), "Method")]
    matches += [
        normalize(cls, method)
        for cls, method in re.findall(
            r'\[HarmonyPatch\s*\(\s*typeof\s*\(\s*([\w\.]+)\s*\)\s*,\s*"([\w\.]+)"\s*(?:,\s*new\s+Type\[\]\s*\{[^\}]*\})?\s*\)\]',
            code
        )
    ]

    # 9. [HarmonyPatch(typeof(Class), nameof(Method))]
    matches += [
        normalize(cls, method)
        for cls, method in re.findall(
            r'\[HarmonyPatch\s*\(\s*typeof\s*\(\s*([\w\.]+)\s*\)\s*,\s*nameof\s*\(\s*([\w\.]+)\s*\)\s*(?:,\s*new\s+Type\[\]\s*\{[^\}]*\})?\s*\)\]',
            code
        )
    ]

    return matches


# Example to test the function on the provided test cases:
test_code = '''
[HarmonyPatch("TLDModCompatibilityChecker.Name")]
[HarmonyPatch("TLDModCompatibilityChecker.NameType", new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch("TLDModCompatibilityChecker", "NameName")]
[HarmonyPatch("TLDModCompatibilityChecker", "NameNameType", new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch("TLDModCompatibilityChecker", nameof(NameNameOf))]
[HarmonyPatch("TLDModCompatibilityChecker", nameof(NameNameOfType), new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch(nameof(TLDModCompatibilityChecker.NameOf))]
[HarmonyPatch(nameof(TLDModCompatibilityChecker.NameOfType), new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch(nameof(TLDModCompatibilityChecker), "NameOfName")]
[HarmonyPatch(nameof(TLDModCompatibilityChecker), "NameOfNameType", new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch(nameof(TLDModCompatibilityChecker), nameof(NameOfNameOf))]
[HarmonyPatch(nameof(TLDModCompatibilityChecker), nameof(NameOfNameOfType), new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch(typeof(TLDModCompatibilityChecker.TypeOf))]
[HarmonyPatch(typeof(TLDModCompatibilityChecker.TypeOfType), new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch(typeof(TLDModCompatibilityChecker), "TypeOfName")]
[HarmonyPatch(typeof(TLDModCompatibilityChecker), "TypeOfNameType", new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch(typeof(TLDModCompatibilityChecker), nameof(TypeOfNameOf))]
[HarmonyPatch(typeof(TLDModCompatibilityChecker), nameof(TypeOfNameOfType), new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch(typeof(TLDModCompatibilityChecker))]
[HarmonyPatch("TLDModCompatibilityChecker", "TLDModCompatibilityChecker.NameNameWithClass")]
[HarmonyPatch("TLDModCompatibilityChecker", "TLDModCompatibilityChecker.NameNameTypeWithClass", new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch("TLDModCompatibilityChecker", nameof(TLDModCompatibilityChecker.NameNameOfWithClass))]
[HarmonyPatch("TLDModCompatibilityChecker", nameof(TLDModCompatibilityChecker.NameNameOfTypeWithClass), new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch(nameof(TLDModCompatibilityChecker), "TLDModCompatibilityChecker.NameOfNameWithClass")]
[HarmonyPatch(nameof(TLDModCompatibilityChecker), "TLDModCompatibilityChecker.NameOfNameTypeWithClass", new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch(nameof(TLDModCompatibilityChecker), nameof(TLDModCompatibilityChecker.NameOfNameOfWithClass))]
[HarmonyPatch(nameof(TLDModCompatibilityChecker), nameof(TLDModCompatibilityChecker.NameOfNameOfTypeWithClass), new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch(typeof(TLDModCompatibilityChecker), "TLDModCompatibilityChecker.TypeOfNameWithClass")]
[HarmonyPatch(typeof(TLDModCompatibilityChecker), "TLDModCompatibilityChecker.TypeOfNameTypeWithClass", new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch(typeof(TLDModCompatibilityChecker), nameof(TLDModCompatibilityChecker.TypeOfNameOfWithClass))]
[HarmonyPatch(typeof(TLDModCompatibilityChecker), nameof(TLDModCompatibilityChecker.TypeOfNameOfTypeWithClass), new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch(typeof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3), nameof(Intermediate2.Intermediate3.TypeOfNameOfWithIntermediates))]
[HarmonyPatch("TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3", "Intermediate2.Intermediate3.NameNameWithIntermediates")]
[HarmonyPatch("TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3", "Intermediate2.Intermediate3.NameNameTypeWithIntermediates", new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch("TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3", nameof(Intermediate2.Intermediate3.NameNameOfWithIntermediates))]
[HarmonyPatch("TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3", nameof(Intermediate2.Intermediate3.NameNameOfTypeWithIntermediates), new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch(nameof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3), "Intermediate2.Intermediate3.NameOfNameWithIntermediates")]
[HarmonyPatch(nameof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3), "Intermediate2.Intermediate3.NameOfNameTypeWithIntermediates", new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch(nameof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3), nameof(Intermediate2.Intermediate3.NameOfNameOfWithIntermediates))]
[HarmonyPatch(nameof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3), nameof(Intermediate2.Intermediate3.NameOfNameOfTypeWithIntermediates), new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch(typeof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3), "Intermediate2.Intermediate3.TypeOfNameWithIntermediates")]
[HarmonyPatch(typeof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3), "Intermediate2.Intermediate3.TypeOfNameTypeWithIntermediates", new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch(typeof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3), nameof(Intermediate2.Intermediate3.TypeOfNameOfWithIntermediates))]
[HarmonyPatch(typeof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3), nameof(Intermediate2.Intermediate3.TypeOfNameOfTypeWithIntermediates), new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch("TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3", "TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3.NameNameWithClassWithIntermediates")]
[HarmonyPatch("TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3", "TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3.NameNameTypeWithClassWithIntermediates", new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch("TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3", nameof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3.NameNameOfWithClassWithIntermediates))]
[HarmonyPatch("TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3", nameof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3.NameNameOfTypeWithClassWithIntermediates), new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch(nameof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3), "TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3.NameOfNameWithClassWithIntermediates")]
[HarmonyPatch(nameof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3), "TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3.NameOfNameTypeWithClassWithIntermediates", new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch(nameof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3), nameof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3.NameOfNameOfWithClassWithIntermediates))]
[HarmonyPatch(nameof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3), nameof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3.NameOfNameOfTypeWithClassWithIntermediates), new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch(typeof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3), "TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3.TypeOfNameWithClassWithIntermediates")]
[HarmonyPatch(typeof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3), "TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3.TypeOfNameTypeWithClassWithIntermediates", new Type[] { typeof(int), typeof(string) })]
[HarmonyPatch(typeof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3), nameof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3.TypeOfNameOfWithClassWithIntermediates))]
[HarmonyPatch(typeof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3), nameof(TLDModCompatibilityChecker.Intermediate1.Intermediate2.Intermediate3.TypeOfNameOfTypeWithClassWithIntermediates), new Type[] { typeof(int), typeof(string) })]
'''

result = extract_harmony_patches_from_code(test_code)
print('\n'.join(result))