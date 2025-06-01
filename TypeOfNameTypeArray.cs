using HarmonyLib;

[HarmonyPatch(typeof(Foo.Bar), "MethodName", new Type[] { typeof(int), typeof(string) })]
public class PatchTypeMethodArgs
{
}