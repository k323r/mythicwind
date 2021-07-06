import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import *
from scipy import integrate
from scipy.integrate import solve_ivp

import argparse


def odeDriveX(t, X, zeta, omega0, omegad_omega0, driving_force_amplitude, force_valsX):
    """
    Driven Harmonic Oscillator ODE, a = 0,4 (zeta), Lookup Table für extern function statt curve fitting wegen genauigkeit
    """
    x, dotx = X  # Input

    # Standard Osc
    # omegad = omegad_omega0 * omega0
    # ddotx = (-1/zeta * dotx) - np.sin(x) + (driving_force_amplitude * np.cos(omegad * t))


    ddotx = -2*zeta*omega0*dotx - omega0**2*x + driving_force_amplitude * calc_scalar(force_valsX, t) #DGL Gleichung

    return [dotx, ddotx]  # return eine Liste von x' und x''


def odeDriveY(t, Y, zeta, omega0, omegad_omega0, driving_force_amplitude, force_valsY):
    """
    Driven Harmonic Oscillator ODE
    """
    y, dotY = Y  # Input
    # Standard Osc
    # omegad = omegad_omega0 * omega0
    # ddoty = ((-1 / zeta) * dotY) - np.sin(y) + (driving_force_amplitude * np.cos( omegad * t))

    ddoty = -2*zeta*omega0*dotY - omega0**2*y + driving_force_amplitude * calc_scalar(force_valsY, t) #DGL Gleichung

    return [dotY, ddoty]  # return eine Liste von x' und x''

def extern_force_data(csvfile, time_unit):

    df = pd.read_csv(csvfile)


    return df


def calc_force_valuesX(df, t_span):

    time = df["time"]
    fx = df["fx"]

    fx_linear = interp1d(time, fx)
    y_il = fx_linear(t_span)
    dfC = pd.DataFrame(list(zip(t_span, y_il)), columns=['time', 'fx'])
    dfC = dfC.set_index(dfC['time'].values)

    return dfC.fx

def calc_force_valuesY(df, t_span):

    time = df["time"]
    fy = df["fy"]

    fx_linear = interp1d(time, fy)
    y_il = fx_linear(t_span)
    dfC = pd.DataFrame(list(zip(t_span, y_il)), columns=['time', 'fy'])
    dfC = dfC.set_index(dfC['time'].values)

    return dfC.fy


def reindex_and_interpolate(df, new_index):
    return df.reindex(df.index | new_index).interpolate(method='index', limit_direction='both').loc[new_index]


def calc_scalar(force_vals, t_point):
    newindex = pd.Float64Index(np.linspace(t_point, t_point, 1))
    force_vals = force_vals.reindex(force_vals.index | newindex)
    force_vals = force_vals.interpolate(method='linear', limit_direction='both')

    force_scalar = force_vals.loc[newindex]

    return force_scalar[t_point]


def ode_solver_with_poincare(t, zeta=2, omega0=0.67, omegad_omega0=1., driving_force_amplitude = 1.04, initial_angle=(np.pi/2), initial_angular_velocity=1.):
    """
    calc with ode solve_ivp
    """
    X0 = [initial_angle,initial_angular_velocity]  # Anfangswerte für gedämpften Osz. -> initial condition
    Y0 = [initial_angle,initial_angular_velocity]
    # The solution is an array with shape (1000 (n_t variable), 2)
    # The first column is amplitude, and the second is velocity
    solX = integrate.solve_ivp(odeDriveX, t, X0, args=(zeta, omega0, omegad_omega0, driving_force_amplitude, force_valsX), method='LSODA', t_eval=t_precision)
    solY = integrate.solve_ivp(odeDriveY, t, Y0, args=(zeta, omega0, omegad_omega0, driving_force_amplitude, force_valsY), method='LSODA', t_eval=t_precision)


    #poincare section
    xX = [solX.y[0, args.end_time * i] for i in range(args.end_time)]  # poincare over position
    yX = [solX.y[1, args.end_time * i] for i in range(args.end_time)]  # poincare over velocity
    poincare_component_listX = [xX, yX]
    xY = [ solX.y[0, args.end_time * i] for i in range(args.end_time)]  # poincare over position
    yY = [ solX.y[1, args.end_time * i] for i in range(args.end_time)]  # poincare over velocity
    poincare_component_listY = [xY, yY]

    return solX, solY, poincare_component_listX, poincare_component_listY

def plot_phaseplane(sol):

    plt.figure()
    plt.title("Phase plane ")
    plt.plot(sol[:, 0], sol[:, 1])
    plt.grid()
    plt.xlabel("$x$, [$m$]")
    plt.ylabel("$\dot{x}$, [$m.s^{-1}$] ")
    plt.show()


def plot_poincare(poincare_list):
    
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(poincare_list[0], poincare_list[1], color='blue', s=0.1)
    plt.xlabel('x', fontsize=15)
    plt.ylabel('y', fontsize=15)
    plt.tick_params(labelsize=15)
    plt.title('The Poincare section')
    plt.show()

def sub_plot_save(solX, solY, poincare_listX, poincare_listY, path, t):

    # plotting deflection and peaks with Datetime
    fig = plt.figure(figsize=(16,12))
    fig.suptitle('2D Oscillator')

    ax = fig.add_subplot(3,3,1)
    ax.plot(solX.y[0, :], solX.y[1, :])
    ax.grid()
    ax.set_xlabel("$x$, [$m$]")
    ax.set_ylabel("$\dot{x}$, [$m.s^{-1}$] ")
    ax.set_title("Phase Plane X-function")

    ax = fig.add_subplot(3, 3, 2)
    ax.plot(solX.t, solX.y[0, :])
    ax.grid()
    ax.set_ylim(-2., 2.)
    ax.set_xlabel("Time, $t$")
    ax.set_ylabel("Amplitude, $a$")
    ax.set_title("Amplitude X-Function")

    ax = fig.add_subplot(3,3,3)
    ax.scatter(poincare_listX[0], poincare_listX[1], color='blue', s=0.1)
    ax.set_xlabel('x', fontsize=15)
    ax.set_ylabel('y', fontsize=15)
    ax.tick_params(labelsize=15)
    ax.set_title('Poincare X-function')

    ax = fig.add_subplot(3, 3, 4)
    ax.plot(solY.y[0, :], solY.y[1, :])
    ax.grid()
    ax.set_xlabel("$y$, [$m$]")
    ax.set_ylabel("$\dot{y}$, [$m.s^{-1}$] ")
    ax.set_title("Phase Plane Y-function")

    ax = fig.add_subplot(3, 3, 5)
    ax.plot(solY.t, solY.y[0, :])
    ax.grid()
    ax.set_ylim(-2., 2.)
    ax.set_xlabel("Time, $t$")
    ax.set_ylabel("Amplitude, $a$")
    ax.set_title("Amplitude Y-Function")

    ax = fig.add_subplot(3, 3, 6)
    ax.scatter(poincare_listY[0], poincare_listY[1], color='blue', s=0.1)
    ax.set_xlabel('x', fontsize=15)
    ax.set_ylabel('y', fontsize=15)
    ax.tick_params(labelsize=15)
    ax.set_title('Poincare Y-function')

    ax = fig.add_subplot(3, 3, 7)
    ax.plot(solX.y[0, :], solY.y[0, :])
    ax.grid()
    ax.set_xlabel("$x$, [$m$]")
    ax.set_ylabel("$y$, [$m$]")
    ax.set_title("X over Y Amplitude")

    ax = fig.add_subplot(3, 3, 8)
    ax.plot(solX.y[1, :], solY.y[1, :])
    ax.grid()
    ax.set_xlabel("$\dot{x}$, [$m.s^{-1}$]")
    ax.set_ylabel("$\dot{y}$, [$m.s^{-1}$] ")
    ax.set_title("X over Y Velocity")

    fig.tight_layout(pad=3.0)
    fig.savefig(path, dpi=300)

if __name__ == '__main__':

    cmd_args = argparse.ArgumentParser()

    cmd_args.add_argument('--initial-angle', type=float,
                          help='initial angle of the forced pendulum', default=0.) #1.5
    cmd_args.add_argument('--initial-angular-velocity', type=float,
                          help='initial velocity of the driven pendulum', default=0.)
    cmd_args.add_argument('--end-time', type=float,
                          help='duration of the simulation', default=10)
    cmd_args.add_argument('--integration-time-step', type=int,
                          help='integration time step', default=100000)


    cmd_args.add_argument('--zeta', type=float,
                          help='damping of the pendulum', default=0.05)
    cmd_args.add_argument('--omega0', type=float,
                          help='forcing function frequency', default=6.28)
    cmd_args.add_argument('--driving-force-amplitude', type=float,
                          help='forcing function amplitude', default=1.00)
    cmd_args.add_argument('--omegad0', type=float,
                          help='factor to scale forcing function frequency', default=1.0)
    cmd_args.add_argument('--force-file', type=argparse.FileType('r'),
                          help='forcing function frequency', default='/Users/mertarat/Documents/GitHub/Input-Output_Data_Pendulum/force-file.csv')

    cmd_args.add_argument('--verbose',
                          default=False, action='store_true', help='')
    cmd_args.add_argument('--show-plots', default=False,
                          action='store_true', help='show plots interactively')
    cmd_args.add_argument('--save-plot-dir', help='directory to save plots', default='/Users/mertarat/Documents/GitHub/Input-Output_Data_Pendulum', type=str)

    args = cmd_args.parse_args()

    t = [0., args.end_time]

    t_precision = np.linspace(0.0, 10.0, args.integration_time_step)

    force = extern_force_data(csvfile=args.force_file, time_unit=t)

    force_valsX = calc_force_valuesX(force, t_precision)

    force_valsY = calc_force_valuesY(force, t_precision)

    if args.verbose:
        print(
            f'running simulation with a resolution of {args.integration_time_step} until t = {args.end_time}')



    sol = ode_solver_with_poincare(t, zeta=args.zeta, omega0=args.omega0, omegad_omega0=args.omegad0, driving_force_amplitude= args.driving_force_amplitude,
                              initial_angle=args.initial_angle, initial_angular_velocity=args.initial_angular_velocity)

    #args.show_plots = True
    #if args.show_plots: plot_phaseplane(sol[0]), plot_phaseplane(sol[1]), plot_poincare(sol[2]), plot_poincare(sol[3])

    if args.save_plot_dir:
        path = f'{args.save_plot_dir}/poincare_zeta:{args.zeta}-omega0:{args.omega0}-A:{args.driving_force_amplitude}.png'
        print(f'path: {path}')
        sub_plot_save(sol[0], sol[1], sol[2], sol[3], path, t)


