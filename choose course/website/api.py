# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from flasgger import Swagger
from flask_restful import Api, Resource

app = Flask(__name__)
swagger = Swagger(app)
api = Api(app)


@app.route("/getInfo/<int:uid>")
def get_info(uid):
    """获取用户信息

    ---
    parameters:
      - name: uid
        in: path
        type: int
        required: true
        default: 1
        description: 用户id

    responses:
      200:
        description: 返回用户信息
        examples:
            {
                code: 0,
                msg: "ok",
                data:
                    {
                        name: "Tom",
                        uid: 1
                    },
            }
    """
    data = {
        "code": 0,
        "msg": "ok",
        "data": {
            "name": "Tom",
            "uid": uid
        }
    }

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
