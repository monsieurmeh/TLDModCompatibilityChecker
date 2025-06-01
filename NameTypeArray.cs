using HarmonyLib;

[HarmonyPatch("TLDModCompatibilityChecker.NameTypeArray", new Type[] { typeof(int), typeof(string) })]
public class PatchMethodArgs
{
}
