using HarmonyLib;

[HarmonyPatch("MethodName", new Type[] { typeof(int), typeof(string) })]
public class PatchMethodArgs
{
}