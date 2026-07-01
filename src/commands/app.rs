use colored::*;
use tabular::{Row, Table};

pub fn run() -> Result<()> {
    let app_name = "mi-app";
    let version = "1.2.0";
    let status = "Instalada";

    // Tabla mejorada
    let mut table = Table::new("{:<} {:<} {:<}");
    table.add_row(Row::new()
        .with_cell("Aplicación".cyan().bold())
        .with_cell("Versión".cyan().bold())
        .with_cell("Estado".cyan().bold())
    );
    table.add_row(Row::new()
        .with_cell(app_name.green())
        .with_cell(version.yellow())
        .with_cell(status.green())
    );

    println!("{}", table);

    Ok(())
}