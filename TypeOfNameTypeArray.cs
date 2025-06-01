using HarmonyLib;

[HarmonyPatch(typeof(TLDModCompatibilityChecker), "TypeOfNameOfArray", new Type[] { typeof(int), typeof(string) })]
public class PatchTypeMethodArgs
{
}
