using HarmonyLib;

[HarmonyPatch(nameof(Foo.Bar.MethodName))]
public class PatchNameofMethodOnly
{
}