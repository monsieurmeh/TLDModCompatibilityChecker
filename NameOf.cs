using HarmonyLib;

[HarmonyPatch(nameof(TLDModCompatibilityChecker.NameOf))]
public class PatchNameofMethodOnly
{
}
