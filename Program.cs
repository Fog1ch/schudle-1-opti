using Mono.Cecil;
using System.Text.Json;
class Program {
 static IEnumerable<TypeDefinition> Walk(IEnumerable<TypeDefinition> ts){foreach(var t in ts){yield return t;foreach(var n in Walk(t.NestedTypes))yield return n;}}
 static object Info(MethodDefinition m)=>new {m.Name,m.FullName,m.IsVirtual,m.IsNewSlot,m.IsFinal,Overrides=m.Overrides.Select(x=>x.FullName).ToArray(),Attributes=m.CustomAttributes.Select(a=>new {Type=a.AttributeType.FullName,Fields=a.Fields.Select(f=>new {f.Name,Value=f.Argument.Value?.ToString()}).ToArray()}).ToArray()};
 static void Main(string[] args){using var a=AssemblyDefinition.ReadAssembly(args[0]); var ts=Walk(a.MainModule.Types).ToArray(); var names=ts.Where(t=>t.Methods.Any(m=>m.Name=="WalkCallback")).Select(t=>t.FullName).ToHashSet(); var dict=ts.ToDictionary(t=>t.FullName); foreach(var n in names.ToArray()){var t=dict[n];while(t.BaseType!=null&&dict.TryGetValue(t.BaseType.FullName,out var b)){names.Add(b.FullName);t=b;}}
 var results=new {CallbackTypes=ts.Where(t=>names.Contains(t.FullName)).Select(t=>new {Type=t.FullName,Base=t.BaseType?.FullName,Methods=t.Methods.Where(m=>m.IsVirtual||m.Name=="WalkCallback").Select(Info).ToArray()}).ToArray(),CacheFields=ts.SelectMany(t=>t.Fields.Where(f=>f.FieldType.FullName.Contains("NPCPathCache")).Select(f=>new {Owner=t.FullName,f.Name,Type=f.FieldType.FullName,f.IsStatic,Attributes=f.CustomAttributes.Select(x=>new {Type=x.AttributeType.FullName,Fields=x.Fields.Select(y=>new{y.Name,Value=y.Argument.Value?.ToString()})})})).ToArray(),WalkResult=ts.Where(t=>t.FullName.EndsWith("NPCMovement/WalkResult")).Select(t=>new{Type=t.FullName,Fields=t.Fields.Select(f=>new{f.Name,Constant=f.HasConstant?f.Constant:null})})};
 File.WriteAllText(args[1],JsonSerializer.Serialize(results,new JsonSerializerOptions{WriteIndented=true}));Console.WriteLine("Metadata written; game assembly read as Cecil data only.");
 }
}
