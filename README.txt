 
# Navegue até a pasta do seu projeto
cd caminho/para/seu/projeto

# Inicialize o repositório Git
git init

# Adicione os arquivos
git add .

# Faça o primeiro commit
git commit -m "Primeiro commit"

# Adicione o repositório remoto do GitHub
git remote add origin https://github.com/seu-usuario/nome-do-repositorio.git

# Envie para o GitHub
git push -u origin main


1. CRIAR ESTRUTURA INICIAL
bash
# Abrir terminal/prompt de comando

# Criar pasta principal
mkdir ProjetoFolhaPagamento
cd ProjetoFolhaPagamento

# Criar solução com nome Luiz
dotnet new sln -n Luiz

# Criar projeto com nome Luan
dotnet new web -n Luan

# Adicionar projeto à solução
dotnet sln Luiz.sln add Luan/Luan.csproj
2. CONFIGURAR PROJETO E PACOTES
bash
# Entrar na pasta do projeto
cd Luan

# Instalar pacotes necessários
dotnet add package Microsoft.EntityFrameworkCore.Sqlite --version 8.0.0
dotnet add package Microsoft.EntityFrameworkCore.Design --version 8.0.0
dotnet add package Swashbuckle.AspNetCore --version 6.4.0

# Criar estrutura de pastas
mkdir Models Data Services DTOs
3. VOLTAR PARA PASTA RAIZ
bash
cd ..
🗂 ESTRUTURA CRIADA ATÉ AGORA
text
ProjetoFolhaPagamento/
├── Luiz.sln
└── Luan/
    ├── Models/
    ├── Data/
    ├── Services/
    ├── DTOs/
    ├── Program.cs
    ├── Luan.csproj
    ├── appsettings.json
    └── Properties/
        └── launchSettings.json
📝 CRIAR ARQUIVOS COM CONTEÚDO
1. Models/FolhaPagamento.cs
bash
# No terminal, dentro da pasta Luan:
cat > Models/FolhaPagamento.cs << 'EOF'
namespace Luan.Models;

public class FolhaPagamento
{
    public int Id { get; set; }
    public string? Nome { get; set; }
    public string? Cpf { get; set; }
    public int Mes { get; set; }
    public int Ano { get; set; }
    public int HorasTrabalhadas { get; set; }
    public decimal ValorHora { get; set; }
    public decimal SalarioBruto { get; set; }
    public decimal ImpostoRenda { get; set; }
    public decimal Inss { get; set; }
    public decimal Fgts { get; set; }
    public decimal SalarioLiquido { get; set; }
}
EOF
2. Data/AppDbContext.cs
bash
cat > Data/AppDbContext.cs << 'EOF'
using Microsoft.EntityFrameworkCore;
using Luan.Models;

namespace Luan.Data;

public class AppDbContext : DbContext
{
    public DbSet<FolhaPagamento> Folhas { get; set; }

    // ⚠️ DATABASE: luiz_luan.db - usar underline entre os nomes!
    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        => optionsBuilder.UseSqlite("Data Source=luiz_luan.db");
    
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // Configurar índice único para evitar duplicatas
        modelBuilder.Entity<FolhaPagamento>()
            .HasIndex(f => new { f.Cpf, f.Mes, f.Ano })
            .IsUnique();
    }
}
EOF
3. Services/CalculadoraService.cs
bash
cat > Services/CalculadoraService.cs << 'EOF'
namespace Luan.Services;

public class CalculadoraService
{
    public static (decimal salarioBruto, decimal impostoRenda, decimal inss, decimal fgts, decimal salarioLiquido) 
        CalcularFolha(decimal horasTrabalhadas, decimal valorHora)
    {
        // Salário Bruto
        decimal salarioBruto = horasTrabalhadas * valorHora;
        
        // Imposto de Renda
        decimal impostoRenda = CalcularIR(salarioBruto);
        
        // INSS
        decimal inss = CalcularINSS(salarioBruto);
        
        // FGTS
        decimal fgts = salarioBruto * 0.08m;
        
        // Salário Líquido
        decimal salarioLiquido = salarioBruto - impostoRenda - inss;
        
        return (salarioBruto, impostoRenda, inss, fgts, salarioLiquido);
    }
    
    private static decimal CalcularIR(decimal salarioBruto)
    {
        return salarioBruto switch
        {
            <= 1903.98m => 0,
            <= 2826.65m => (salarioBruto * 0.075m) - 142.80m,
            <= 3751.05m => (salarioBruto * 0.15m) - 354.80m,
            <= 4664.68m => (salarioBruto * 0.225m) - 636.13m,
            _ => (salarioBruto * 0.275m) - 869.36m
        };
    }
    
    private static decimal CalcularINSS(decimal salarioBruto)
    {
        return salarioBruto switch
        {
            <= 1693.72m => salarioBruto * 0.08m,
            <= 2822.90m => salarioBruto * 0.09m,
            <= 5645.80m => salarioBruto * 0.11m,
            _ => 621.03m
        };
    }
}
EOF
4. DTOs/FolhaPagamentoDTO.cs
bash
cat > DTOs/FolhaPagamentoDTO.cs << 'EOF'
namespace Luan.DTOs;

public record FolhaPagamentoRequest(
    string Nome,
    string Cpf,
    int Mes,
    int Ano,
    int HorasTrabalhadas,
    decimal ValorHora
);

public record FolhaPagamentoResponse(
    int Id,
    string Nome,
    string Cpf,
    int Mes,
    int Ano,
    int HorasTrabalhadas,
    decimal ValorHora,
    decimal SalarioBruto,
    decimal ImpostoRenda,
    decimal Inss,
    decimal Fgts,
    decimal SalarioLiquido
);

public record TotalLiquidoResponse(decimal TotalLiquido);
EOF
5. Program.cs (SUBSTITUIR TODO CONTEÚDO)
bash
cat > Program.cs << 'EOF'
using Microsoft.EntityFrameworkCore;
using Luan.Data;
using Luan.Models;
using Luan.Services;
using Luan.DTOs;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddDbContext<AppDbContext>();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

// ✅ FUNCIONALIDADE 1 - Cadastrar Folha
app.MapPost("/api/folha/cadastrar", async (FolhaPagamentoRequest request, AppDbContext context) =>
{
    if (request.Mes < 1 || request.Mes > 12)
        return Results.BadRequest("Mês deve estar entre 1 e 12");
    
    if (request.Ano < 2000)
        return Results.BadRequest("Ano deve ser maior ou igual a 2000");
    
    bool folhaExistente = await context.Folhas
        .AnyAsync(f => f.Cpf == request.Cpf && f.Mes == request.Mes && f.Ano == request.Ano);
    
    if (folhaExistente)
        return Results.BadRequest("Já existe uma folha para este CPF, mês e ano");
    
    var calculos = CalculadoraService.CalcularFolha(request.HorasTrabalhadas, request.ValorHora);
    
    var folha = new FolhaPagamento
    {
        Nome = request.Nome,
        Cpf = request.Cpf,
        Mes = request.Mes,
        Ano = request.Ano,
        HorasTrabalhadas = request.HorasTrabalhadas,
        ValorHora = request.ValorHora,
        SalarioBruto = calculos.salarioBruto,
        ImpostoRenda = calculos.impostoRenda,
        Inss = calculos.inss,
        Fgts = calculos.fgts,
        SalarioLiquido = calculos.salarioLiquido
    };
    
    context.Folhas.Add(folha);
    await context.SaveChangesAsync();
    
    var response = new FolhaPagamentoResponse(
        folha.Id,
        folha.Nome!,
        folha.Cpf!,
        folha.Mes,
        folha.Ano,
        folha.HorasTrabalhadas,
        folha.ValorHora,
        folha.SalarioBruto,
        folha.ImpostoRenda,
        folha.Inss,
        folha.Fgts,
        folha.SalarioLiquido
    );
    
    return Results.Created($"/api/folha/{folha.Id}", response);
})
.WithName("CadastrarFolha")
.WithOpenApi();

// ✅ FUNCIONALIDADE 2 - Listar Folhas
app.MapGet("/api/folha/listar", async (AppDbContext context) =>
{
    var folhas = await context.Folhas.ToListAsync();
    
    if (!folhas.Any())
        return Results.NotFound("Nenhuma folha de pagamento encontrada");
    
    var response = folhas.Select(f => new FolhaPagamentoResponse(
        f.Id,
        f.Nome!,
        f.Cpf!,
        f.Mes,
        f.Ano,
        f.HorasTrabalhadas,
        f.ValorHora,
        f.SalarioBruto,
        f.ImpostoRenda,
        f.Inss,
        f.Fgts,
        f.SalarioLiquido
    ));
    
    return Results.Ok(response);
})
.WithName("ListarFolhas")
.WithOpenApi();

// ✅ FUNCIONALIDADE 3 - Buscar Folha por CPF, Mês e Ano
app.MapGet("/api/folha/buscar/{cpf}/{mes}/{ano}", async (string cpf, int mes, int ano, AppDbContext context) =>
{
    var folha = await context.Folhas
        .FirstOrDefaultAsync(f => f.Cpf == cpf && f.Mes == mes && f.Ano == ano);
    
    if (folha is null)
        return Results.NotFound("Folha de pagamento não encontrada");
    
    var response = new FolhaPagamentoResponse(
        folha.Id,
        folha.Nome!,
        folha.Cpf!,
        folha.Mes,
        folha.Ano,
        folha.HorasTrabalhadas,
        folha.ValorHora,
        folha.SalarioBruto,
        folha.ImpostoRenda,
        folha.Inss,
        folha.Fgts,
        folha.SalarioLiquido
    );
    
    return Results.Ok(response);
})
.WithName("BuscarFolha")
.WithOpenApi();

// ✅ FUNCIONALIDADE 4 - Remover Folha
app.MapDelete("/api/folha/remover/{cpf}/{mes}/{ano}", async (string cpf, int mes, int ano, AppDbContext context) =>
{
    var folha = await context.Folhas
        .FirstOrDefaultAsync(f => f.Cpf == cpf && f.Mes == mes && f.Ano == ano);
    
    if (folha is null)
        return Results.NotFound("Folha de pagamento não encontrada");
    
    context.Folhas.Remove(folha);
    await context.SaveChangesAsync();
    
    return Results.Ok("Folha removida com sucesso");
})
.WithName("RemoverFolha")
.WithOpenApi();

// ✅ FUNCIONALIDADE 5 - Total Líquido
app.MapGet("/api/folha/total-liquido", async (AppDbContext context) =>
{
    var folhas = await context.Folhas.ToListAsync();
    
    if (!folhas.Any())
        return Results.NotFound("Nenhuma folha de pagamento encontrada");
    
    decimal totalLiquido = folhas.Sum(f => f.SalarioLiquido);
    
    var response = new TotalLiquidoResponse(Math.Round(totalLiquido, 2));
    
    return Results.Ok(response);
})
.WithName("TotalLiquido")
.WithOpenApi();

// Inicializar banco de dados
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.EnsureCreated();
}

app.Run();
EOF
🚀 EXECUTANDO O PROJETO
Voltar para pasta raiz e executar:
bash
# Voltar para pasta raiz (onde está Luiz.sln)
cd ..

# Executar projeto
dotnet run --project Luan

# OU executar de dentro da pasta Luan:
# dotnet run
✅ RESULTADO ESPERADO:
text
info: Microsoft.Hosting.Lifetime[14]
      Now listening on: https://localhost:7000
info: Microsoft.Hosting.Lifetime[14]
      Now listening on: http://localhost:5000
🌐 TESTANDO A APLICAÇÃO
Acesse no navegador:
Swagger UI: https://localhost:7000/swagger

API Direct: https://localhost:7000/api/folha/listar

Teste o cadastro via Swagger:
json
{
  "nome": "Luiz Silva",
  "cpf": "123.456.789-00",
  "mes": 10,
  "ano": 2025,
  "horasTrabalhadas": 160,
  "valorHora": 50
}
📁 ESTRUTURA FINAL CONFIRMADA
text
ProjetoFolhaPagamento/
├── Luiz.sln                 ← SOLUÇÃO (nome: Luiz)
└── Luan/                    ← PROJETO (nome: Luan)
    ├── Models/
    │   └── FolhaPagamento.cs
    ├── Data/
    │   └── AppDbContext.cs
    ├── Services/
    │   └── CalculadoraService.cs
    ├── DTOs/
    │   └── FolhaPagamentoDTO.cs
    ├── Program.cs
    ├── Luan.csproj
    ├── luiz_luan.db         ← DATABASE (será criado)
    ├── appsettings.json
    └── Properties/
        └── launchSettings.json
✅ VERIFICAÇÃO FINAL
Execute estes comandos para validar:
bash
# Na pasta raiz (ProjetoFolhaPagamento)
dotnet build
dotnet run --project Luan
Verifique se:
✅ Compila sem erros

✅ Sobe na porta 7000

✅ Swagger abre normalmente

✅ Arquivo luiz_luan.db é criado

✅ Todos endpoints aparecem no Swagger



### O Conceito: API e Webhooks


  Para que seu bot converse no WhatsApp, ele precisa se tornar um serviço na internet. A comunicação funciona assim:
  1.  Usuário Manda Mensagem: O cliente envia uma mensagem para seu número de WhatsApp Business.
  2.  WhatsApp Envia para Você: O WhatsApp não executa seu código. Em vez disso, ele envia os dados da mensagem (quem mandou, o que disse) para
   uma URL pública sua. Essa notificação é chamada de Webhook.
  3.  Seu Bot Processa: Seu código, agora rodando em um servidor, recebe essa notificação, processa a mensagem com a lógica que criamos e gera
  uma resposta.
  4.  Você Envia para o WhatsApp: Seu código então usa a API do WhatsApp para enviar a resposta de volta para o usuário.

  ### Como Fazer na Prática:


  1. API do WhatsApp Business:
  A Meta (dona do WhatsApp) oferece uma API para isso. A maneira mais fácil de acessá-la é através de um Provedor de Soluções de Negócios
  (BSP), como a Twilio ou a MessageBird. Eles cuidam da infraestrutura e te dão uma API mais simples de usar. Haverá custos associados,
  geralmente por conversa.

  2. Mudanças no seu Código:
  A arquitetura do seu bot precisa evoluir para um aplicativo web.


   * Adeus, `main.py`: O loop while True e o input() no seu main.py não funcionarão mais. Você precisará substituí-lo por um pequeno servidor
     web usando um framework como Flask ou FastAPI. Esse servidor terá uma rota (ex: /webhook) para receber as mensagens do WhatsApp.
   * Múltiplos Usuários (Crítico!): Seu bot atual guarda o estado da conversa (self.estado_conversa) para uma única pessoa. No WhatsApp, várias
     pessoas falarão com ele ao mesmo tempo. Você precisa adaptar a classe Chatbot para guardar o estado de cada usuário separadamente.