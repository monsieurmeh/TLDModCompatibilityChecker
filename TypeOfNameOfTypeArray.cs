using HarmonyLib;

[HarmonyPatch(typeof(Foo.Bar), nameof(Foo.Bar.MethodName), new Type[] { typeof(int), typeof(string) })]
public class PatchTypeNameofArgs
{
}