CREATE TABLE blade_landings (
    blade_installation_id INT PRIMARY KEY,
    blade_landing_epoch INT NOT NULL,
    blade_disconnected_epoch INT NOT NULL,
    blade_disconnected_epoch - blade_landing_epoch AS blade_connected_duration,
    sbitroot_ax INT NOT NULL,
    helihoist_ax INT NOT NULL,
    FOREIGN KEY (blade_installation_id) REFERENCES blade_installations(blade_installation_id));


CREATE view blade_landings_full AS
	SELECT
		blade_installation_id,
        turbine_id,
		blade_number,
		blade_installation_attempt,
		blade_installation_start_epoch,
		blade_landing_epoch,
		blade_disconnected_epoch,
		blade_connected_duration_seconds,
		blade_installation_end_epoch
	FROM blade_landings
	JOIN blade_installations USING (blade_installation_id);