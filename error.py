from configuration import botErrorAlert


def botFailed(asset, message):
    if botErrorAlert == 'email':
        # todo email
        exit(1)
    else:
        if asset:
            print('Asset: ' + asset)

        print(message)
        exit(1)
