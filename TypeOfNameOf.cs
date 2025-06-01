using HarmonyLib;

[HarmonyPatch(typeof(TLDModCompatibilityChecker), nameof(TLDModCompatibilityChecker.TypeOfNameOf))]
public class PatchTypeAndNameof
{
}
