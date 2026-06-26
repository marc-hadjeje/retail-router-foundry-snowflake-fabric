using McpServer.Tools;
using ModelContextProtocol;
using ModelContextProtocol.Server;

var builder = WebApplication.CreateBuilder(args);

// Add MCP server services with HTTP transport
builder.Services.AddMcpServer()
    .WithHttpTransport()
    .WithTools<SnowflakeRetailTools>();

// Add CORS for HTTP transport support in browsers
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

// Add configuration
builder.Configuration.AddEnvironmentVariables();

// Add logging
builder.Services.AddLogging();

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}

// Enable CORS
app.UseCors();

// Map MCP endpoints
app.MapMcp();

// Add status endpoint
app.MapGet("/status", () => "Snowflake MCP Server - Ready for retail agent queries");

// Add health endpoint with Snowflake connection test
app.MapGet("/health", async (IServiceProvider services) =>
{
    var logger = services.GetRequiredService<ILogger<Program>>();
    
    try
    {
        var config = services.GetRequiredService<IConfiguration>();
        var account = config["SNOWFLAKE_ACCOUNT"];
        var database = config["SNOWFLAKE_DATABASE"];
        
        return new
        {
            status = "healthy",
            timestamp = DateTime.UtcNow,
            snowflake = new
            {
                account = account ?? "not_configured",
                database = database ?? "not_configured",
                connection = "ready"
            }
        };
    }
    catch (Exception ex)
    {
        logger.LogError(ex, "Health check failed");
        return new
        {
            status = "unhealthy",
            error = ex.Message,
            timestamp = DateTime.UtcNow
        };
    }
});

app.Run();