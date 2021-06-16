import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scipy import integrate

import argparse


def odeDriveX(X, t, zeta, omega0, omegad_omega0, driving_force_amplitude):
    """
    Driven Harmonic Oscillator ODE
    """
    x, dotx = X  # Input
    
    omegad = omegad_omega0 * omega0
    # ddotx = -2*zeta*omega0*dotx - omega0**2*x + F_m * np.sin(omegad * t) #DGL Gleichung
    ddotx = (-1/zeta * dotx) - np.sin(x) + (driving_force_amplitude * np.cos(omegad * t))
    return [dotx, ddotx]  # return eine Liste von x' und x''


def odeDriveY(Y, t, zeta, omega0, omegad_omega0, driving_force_amplitude):
    """
    Driven Harmonic Oscillator ODE
    """
    y, dotY = Y  # Input

    omegad = omegad_omega0 * omega0
    # ddotx = -2*zeta*omega0*dotx - omega0**2*x + F_m * np.sin(omegad * t) #DGL Gleichung
    ddoty = (-1 / zeta * dotY) - np.sin(y) + (driving_force_amplitude * np.cos(omegad * t))
    return [dotY, ddoty]  # return eine Liste von x' und x''

'''def extern_force_data(csvfile):
    df = pd.read_csv(csvfile)
    function_list = np.asarray(df, dtype=np.float64, order='C')


    return function_list'''



def phaseplane_poincare(t, zeta=2, omega0=0.67, omegad_omega0=1., driving_force_amplitude = 1.04, initial_angle=(np.pi/2), initial_angular_velocity=1.,):
    """
    Update function and calc with odeint
    """
    X0 = [initial_angle,initial_angular_velocity]  # Anfangswerte für gedämpften Osz. -> initial condition
    Y0 = [initial_angle,initial_angular_velocity]
    # The solution is an array with shape (1000 (n_t variable), 2)
    # The first column is amplitude, and the second is velocity
    solX = integrate.odeint(odeDriveX, X0, t, args=(zeta, omega0, omegad_omega0, driving_force_amplitude))
    solY = integrate.odeint(odeDriveY, Y0, t, args=(zeta, omega0, omegad_omega0, driving_force_amplitude))


    #poincare section
    xX = [solX[args.end_time * i, 0] for i in range(args.end_time)]  # poincare over position
    yX = [solX[args.end_time * i, 1] for i in range(args.end_time)]  # poincare over velocity
    poincare_component_listX = [xX, yX]
    xY = [solX[args.end_time * i, 0] for i in range(args.end_time)]  # poincare over position
    yY = [solX[args.end_time * i, 1] for i in range(args.end_time)]  # poincare over velocity
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
    ax.plot(solX[:, 0], solX[:, 1])
    ax.grid()
    ax.set_xlabel("$x$, [$m$]")
    ax.set_ylabel("$\dot{x}$, [$m.s^{-1}$] ")
    ax.set_title("Phase Plane X-function")

    ax = fig.add_subplot(3, 3, 2)
    ax.plot(t, solX[:, 0])
    ax.grid()
    ax.set_ylim(-10., 10.)
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
    ax.plot(solY[:, 0], solY[:, 1])
    ax.grid()
    ax.set_xlabel("$y$, [$m$]")
    ax.set_ylabel("$\dot{y}$, [$m.s^{-1}$] ")
    ax.set_title("Phase Plane Y-function")

    ax = fig.add_subplot(3, 3, 5)
    ax.plot(t, solY[:, 0])
    ax.grid()
    ax.set_ylim(-10., 10.)
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
    ax.plot(solX[:, 0], solY[:, 0])
    ax.grid()
    ax.set_xlabel("$x$, [$m$]")
    ax.set_ylabel("$y$, [$m$]")
    ax.set_title("X over Y Amplitude")

    ax = fig.add_subplot(3, 3, 8)
    ax.plot(solX[:, 1], solY[:, 1])
    ax.grid()
    ax.set_xlabel("$\dot{x}$, [$m.s^{-1}$]")
    ax.set_ylabel("$\dot{y}$, [$m.s^{-1}$] ")
    ax.set_title("X over Y Velocity")

    fig.tight_layout(pad=3.0)
    fig.savefig(path, dpi=300)

if __name__ == '__main__':

    cmd_args = argparse.ArgumentParser()

    cmd_args.add_argument('--initial-angle', type=float,
                          help='initial angle of the forced penulum', default=1.5)
    cmd_args.add_argument('--initial-angular-velocity', type=float,
                          help='initial velocity of the driven pendulum', default=0.)
    cmd_args.add_argument('--end-time', type=int,
                          help='duration of the simulation', default=100)
    cmd_args.add_argument('--integration-time-step', type=float,
                          help='integration time step', default=0.01)


    cmd_args.add_argument('--zeta', type=float,
                          help='damping of the pendulum', default=2.0)
    cmd_args.add_argument('--omega0', type=float,
                          help='forcing function frequency', default=0.67)
    cmd_args.add_argument('--driving-force-amplitude', type=float,
                          help='forcing function amplitude', default=1.04)
    cmd_args.add_argument('--omegad0', type=float,
                          help='factor to scale forcing function frequency', default=1.0)
    '''cmd_args.add_argument('--force-file', type=argparse.FileType('r'),
                          help='forcing function frequency', default='/Users/mertarat/Documents/GitHub/Output_Data_Pendulum/force-file.csv')'''

    cmd_args.add_argument('--verbose',
                          default=False, action='store_true', help='')
    cmd_args.add_argument('--show-plots', default=False,
                          action='store_true', help='show plots interactively')
    cmd_args.add_argument('--save-plot-dir', help='directory to save plots', default='/Users/mertarat/Documents/GitHub/Output_Data_Pendulum', type=str)

    args = cmd_args.parse_args()


    t = np.linspace(0, args.end_time, num=int(
        args.end_time / args.integration_time_step))


    if args.verbose:
        print(
            f'running simulation with a resolution of {args.integration_time_step} until t = {args.end_time}')



    sol = phaseplane_poincare(t, zeta=args.zeta, omega0=args.omega0, omegad_omega0=args.omegad0, driving_force_amplitude= args.driving_force_amplitude,
                              initial_angle=args.initial_angle, initial_angular_velocity=args.initial_angular_velocity)

    #args.show_plots = True
    if args.show_plots: plot_phaseplane(sol[0]), plot_phaseplane(sol[1]), plot_poincare(sol[2]), plot_poincare(sol[3])

    if args.save_plot_dir:
        path = f'{args.save_plot_dir}/poincare_zeta:{args.zeta}-omega0:{args.omega0}-A:{args.driving_force_amplitude}.png'
        print(f'path: {path}')
        sub_plot_save(sol[0], sol[1], sol[2], sol[3], path, t)


