using HarmonyLib;

[HarmonyPatch(typeof(Foo.Bar), nameof(Foo.Bar.MethodName))]
public class PatchTypeAndNameof
{
}