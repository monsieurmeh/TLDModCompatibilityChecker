using HarmonyLib;

[HarmonyPatch(typeof(Foo.Bar), "MethodName")]
public class PatchTypeAndMethod
{
}