using HarmonyLib;

[HarmonyPatch(typeof(TLDModCompatibilityChecker), "TypeOfNameTypeArray", new Type[] { typeof(int), typeof(string) })]
public class PatchTypeMethodArgs
{
}
