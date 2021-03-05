CREATE TABLE turbines (
    turbine_id INT PRIMARY KEY,                 -- UNIQUE NOT NULL
    t_name TEXT NOT NULL,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    turbine_install_start REAL NOT NULL,
    turbine_install_stop REAL NOT NULL,
    cell_install_start REAL NOT NULL,
    cell_install_stop REAL NOT NULL,
    total_start REAL NOT NULL,
    total_stop REAL NOT NULL);

CREATE TABLE blade_installations (
    blade_installation_id INT PRIMARY KEY,
    turbine_id INT NOT NULL,
    blade_number INT NOT NULL,
    blade_installation_start REAL NOT NULL,
    blade_installation_stop REAL NOT NULL,
    blade_installation_is_successful INT NOT NULL CHECK(
        blade_installation_is_successful = 0
        OR blade_installation_is_successful = 1),
    FOREIGN KEY (turbine_id) REFERENCES turbines (turbine_id));

CREATE VIEW turbines_full_info AS
    SELECT
        turbine_id,
        t_name,
        lat,
        lon,
        turbine_install_start,
        turbine_install_stop,
        turbine_install_stop - turbine_install_start AS turbine_install_duration,
        cell_install_start,
        cell_install_stop,
        total_start,
        total_stop,
        blade_installation_id,
        blade_number,
        blade_installation_start,
        blade_installation_stop,
        blade_installation_is_successful
    FROM
        turbines
        JOIN blade_installations USING (turbine_id);

CREATE VIEW blade_installation_success AS
    SELECT
        turbine_id,
        t_name,
        blade_installation_id,
        blade_number,
        blade_installation_start,
        blade_installation_stop
    FROM
        turbines_full_info
    WHERE
        blade_installation_is_successful = 1;

-- INT(EGER) REAL TEXT BLOB
