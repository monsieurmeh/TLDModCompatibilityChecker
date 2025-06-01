using HarmonyLib;

[HarmonyPatch(typeof(TLDModCompatibilityChecker), nameof(TLDModCompatibilityChecker.TypeOfNameOfArray), new Type[] { typeof(int), typeof(string) })]
public class PatchTypeNameofArgs
{
}
