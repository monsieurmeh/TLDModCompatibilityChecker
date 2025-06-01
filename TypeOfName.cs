using HarmonyLib;

[HarmonyPatch(typeof(TLDModCompatibilityChecker), "TypeOfName")]
public class PatchTypeAndMethod
{
}
