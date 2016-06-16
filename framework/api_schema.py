schema = {
  "type": "object",
  "properties": {
    "service": {
      "type": "string"
    },
    "cpu": {
      "type": "integer"
    },
    "mem": {
      "type": "integer"
    },
    "hosts": {
      "type": "array",
      "items": [
        {
          "type": "string"
        },
        {
          "type": "string"
        }
      ]
    },
    "ssh": {
      "type": "object",
      "properties": {
        "username": {
          "type": "string"
        },
        "password": {
          "type": "string"
        },
        "identity_file": {
          "type": "string"
        }
      }
    },
    "loglevel": {
      "type": "string"
    },
    "failfast": {
      "type": "boolean"
    },
    "failures": {
      "type": "array",
      "items": [
        {
          "type": "object",
          "properties": {
            "name": {
              "type": "string"
            },
            "inducer": {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            },
            "reverter": {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            },
            "healthcheck": {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            }
          }
        },
        {
          "type": "object",
          "properties": {
            "name": {
              "type": "string"
            },
            "inducer": {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            },
            "reverter": {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            },
            "healthcheck": {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            }
          }
        }
      ]
    }
  },
  "required": [
    "service",
    "cpu",
    "mem",
    "hosts",
    "ssh",
    "loglevel",
    "failfast",
    "failures"
  ]
}
