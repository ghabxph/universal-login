from flask import request
from flask import Response
import os


class AssetsController:

    @staticmethod
    def get():
        asset = '/html/%s' % request.values.get('file')

        # Basic security check
        if os.path.commonprefix((os.path.realpath(asset), '/html/')) != '/html/':
            return Response('Asset not found.', mimetype='text/plain'), 404

        try:
            with open(asset) as asset_file:

                # Returns JS
                if asset.endswith('.js'):
                    return Response(asset_file.read(), mimetype='application/javascript'), 200

                # Returns CSS
                if asset.endswith('.css'):
                    return Response(asset_file.read(), mimetype='text/css'), 200

            # Asset not found
            return Response('Asset not found.', mimetype='text/plain'), 404

        # Returns 404 if file does not exist.
        except FileNotFoundError:

            # Asset not found
            return Response('Asset not found.', mimetype='text/plain'), 404
