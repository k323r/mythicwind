import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--substract-gps', help='test', type=str)

    args = parser.parse_args()

    print(type(args.substract_gps))

    print(args.substract_gps[0])

    if args.substract_gps:
        try:
            lat, lon = args.substract_gps.split(',')
        except:
            print('failed to parse tuple')

        try:
            lat = float(lat)
            lon = float(lon)
        except:
            print('failed to cast float from command line tuple')

        print(f'lat {lat} lon {lon}')

