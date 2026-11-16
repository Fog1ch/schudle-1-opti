from pathlib import Path
import subprocess,json
r=Path(__file__).parent; d=r/'metadata-reader'
(d/'Reader.csproj').write_text('''<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings></PropertyGroup><ItemGroup><Reference Include="Mono.Cecil"><HintPath>../analyzer/bin/Release/net8.0/Mono.Cecil.dll</HintPath></Reference></ItemGroup></Project>''')
(d/'NuGet.Config').write_text('<configuration><packageSources><clear /></packageSources></configuration>')
a=subprocess.run(['dotnet','build',str(d/'Reader.csproj'),'-c','Release','--configfile',str(d/'NuGet.Config')],capture_output=True,text=True)
print(a.stdout,a.stderr);assert a.returncode==0
b=subprocess.run(['dotnet',str(d/'bin/Release/net8.0/Reader.dll'),r'B:\Schedule I\MelonLoader\Dependencies\Il2CppAssemblyGenerator\Cpp2IL\cpp2il_out\Assembly-CSharp.dll',str(r/'callback-metadata.json')],capture_output=True,text=True)
print(b.stdout,b.stderr);assert b.returncode==0
j=json.loads((r/'callback-metadata.json').read_text())
for t in j['CallbackTypes']:
 for m in t['Methods']:
  if m['Name']=='WalkCallback': print(t['Type'],t['Base'],m)
print('CACHE FIELDS',j['CacheFields']);print('ENUM',j['WalkResult'])
