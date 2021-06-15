import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scipy import integrate

import argparse


def odeDrive(X, t, zeta, omega0, omegad_omega0, driving_force_amplitude):
    """
    Driven Harmonic Oscillator ODE
    """
    x, dotx = X  # Input
    
    omegad = omegad_omega0 * omega0
    # ddotx = -2*zeta*omega0*dotx - omega0**2*x + F_m * np.sin(omegad * t) #DGL Gleichung
    ddotx = (-1/zeta * dotx) - np.sin(x) + (driving_force_amplitude * np.cos(omegad * t))
    return [dotx, ddotx]  # return eine Liste von x' und x''


# def phaseplane(args):
#    pass


def phaseplane_poincare(t, zeta=2, omega0=0.67, omegad_omega0=1., driving_force_amplitude = 1.04, initial_angle=(np.pi/2), initial_angular_velocity=1.,):
    """
    Update function and calc with odeint
    """
    X0 = [initial_angle,initial_angular_velocity]  # Anfangswerte für gedämpften Osz. -> initial condition

    # The solution is an array with shape (1000 (n_t variable), 2)
    # The first column is amplitude, and the second is velocity
    sol = integrate.odeint(odeDrive, X0, t, args=(zeta, omega0, omegad_omega0, driving_force_amplitude))

    #poincare section
    x = [sol[args.end_time * i, 0] for i in range(args.end_time)]  # poincare over position
    y = [sol[args.end_time * i, 1] for i in range(args.end_time)]  # poincare over velocity
    poincare_component_list = [x, y]

    return sol, poincare_component_list

def plot_phaseplane(sol):

    plt.figure()
    plt.title("Phase plane ")
    plt.plot(sol[:, 0], sol[:, 1])
    plt.grid()
    plt.xlabel("$x$, [$m$]")
    plt.ylabel("$\dot{x}$, [$m.s^{-1}$] ")
    plt.show()

'''
def poincare(zeta=2, omega0=0.67, omegad_omega0=1., driving_force_amplitude = 1.04, initial_angle=(np.pi/2), initial_angular_velocity=1.):


    # We will generate a solution at 16000000(4000*4000) evenly spaced samples in the interval
    # 0 <= t <= 4000
    t_pm = np.linspace(0, 4000 * (2*np.pi) / omega0, num=16000000)

    # initial conditions
    X0 = [args.initial_angle, args.driv]

    # Poincare calc (4000, because of t_pm)
    xs = integrate.odeint(odeDrive, X0, t_pm, args=(zeta, omega0, omegad_omega0, driving_force_amplitude))
    x = [xs[4000*i, 0] for i in range(4000)]  # poincare over position
    y = [xs[4000*i, 1] for i in range(4000)]  # poincare over velocity
    poincare_component_list = [x,y]

    return poincare_component_list'''

def plot_poincare(poincare_list):
    
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(poincare_list[0], poincare_list[1], color='blue', s=0.1)
    plt.xlabel('x', fontsize=15)
    plt.ylabel('y', fontsize=15)
    plt.tick_params(labelsize=15)
    plt.title('The Poincare section')
    plt.show()

def sub_plot_save(sol, poincare_list, path):

    # plotting deflection and peaks with Datetime
    fig = plt.figure(figsize=(16,12))
    fig.suptitle('2D Oscillator')


    ax = fig.add_subplot(3,3,1)
    ax.plot(sol[:, 0], sol[:, 1])
    ax.grid()
    ax.set_xlabel("$x$, [$m$]")
    ax.set_ylabel("$\dot{x}$, [$m.s^{-1}$] ")
    ax.set_title("Phase Plane")

    ax = fig.add_subplot(3,3,2)
    ax.scatter(poincare_list[0], poincare_list[1], color='blue', s=0.1)
    ax.set_xlabel('x', fontsize=15)
    ax.set_ylabel('y', fontsize=15)
    ax.tick_params(labelsize=15)
    ax.set_title('Poincare')

    ax = fig.add_subplot(3, 3, 3, projection='3d')
    X = sol[:, 0]
    Y = sol[:, 0]
    X, Y = np.meshgrid(X, Y)
    R = X+Y
    Z = R

    surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
                           linewidth=0, antialiased=False)

    ax.set_zlim(-1, 1)
    ax.set_xlabel("X Amplitude")
    ax.set_ylabel("Y Amplitude")
    ax.set_title("3D Amplitude")
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
    if args.show_plots: plot_phaseplane(sol[0]), plot_poincare(sol[1])

    if args.save_plot_dir:
        path = f'{args.save_plot_dir}/poincare_zeta:{args.zeta}-omega0:{args.omega0}-A:{args.driving_force_amplitude}.png'
        print(f'path: {path}')
        sub_plot_save(sol[0], sol[1], path)


