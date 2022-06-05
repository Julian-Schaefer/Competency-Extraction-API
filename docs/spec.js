var spec = {
  "openapi": "3.0.0",
  "info": {
    "description": "This is our AWT project server. You can query competencies and courses here.",
    "version": "1.0.0",
    "title": "Competency Extraction",
    "license": {
      "name": "Apache 2.0",
      "url": "http://www.apache.org/licenses/LICENSE-2.0.html"
    }
  },
  "tags": [
    {
      "name": "competency",
      "description": "Add and query competencies",
      "externalDocs": {
        "description": "EU ESCO",
        "url": "https://esco.ec.europa.eu/en/classification/skill?uri=http%3A%2F%2Fdata.europa.eu%2Fesco%2Fskill%2FA1.1.0"
      }
    },
    {
      "name": "course",
      "description": "Add and query courses"
    },
    {
      "name": "relation",
      "description": "Add relationships between courses and competencies"
    }
  ],
  "paths": {
    "/competency/{competencyName}": {
      "post": {
        "tags": [
          "competency"
        ],
        "summary": "Add a new competency",
        "description": "Add a new competency",
        "operationId": "addCompetency",
        "parameters": [
          {
            "in": "path",
            "name": "competencyName",
            "description": "Name of competency to be added",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Competency was added successfully.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Competency"
                }
              }
            }
          },
          "400": {
            "description": "Invalid input"
          }
        },
        "requestBody": {
          "description": "Add a new competency",
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CompetencyBody"
              }
            }
          }
        }
      }
    },
    "/course/{courseName}": {
      "post": {
        "tags": [
          "course"
        ],
        "summary": "Add a new course",
        "description": "Add a new course",
        "operationId": "addCourse",
        "parameters": [
          {
            "in": "path",
            "name": "courseName",
            "description": "Name of course to be added",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Course was added successfully.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Course"
                }
              }
            }
          },
          "400": {
            "description": "Invalid input"
          }
        },
        "requestBody": {
          "description": "Add a new course",
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CourseBody"
              }
            }
          }
        }
      }
    },
    "/course": {
      "get": {
        "tags": [
          "course"
        ],
        "summary": "Query for courses",
        "description": "Query for courses",
        "operationId": "retrieveCourses",
        "responses": {
          "200": {
            "description": "Query result for courses.",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/Course"
                  }
                }
              }
            }
          },
          "400": {
            "description": "Invalid input"
          }
        }
      }
    },
    "/course/{competencyId}": {
      "get": {
        "tags": [
          "course"
        ],
        "summary": "Query for courses",
        "description": "Query for courses",
        "operationId": "retrieveCoursesByCompetency",
        "responses": {
          "200": {
            "description": "Query result for courses.",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/Course"
                  }
                }
              }
            }
          },
          "400": {
            "description": "Invalid input"
          }
        },
        "parameters": [
          {
            "in": "path",
            "name": "competencyId",
            "description": "Filter courses by competency",
            "required": true,
            "schema": {
              "$ref": "#/components/schemas/CompetencyId"
            }
          }
        ]
      }
    },
    "/competency": {
      "get": {
        "tags": [
          "competency"
        ],
        "summary": "Query for competencies",
        "description": "Query for competencies",
        "operationId": "retrieveCompetencies",
        "responses": {
          "200": {
            "description": "Query result for competencies.",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/Competency"
                  }
                }
              }
            }
          },
          "400": {
            "description": "Invalid input"
          }
        }
      }
    },
    "/competency/{courseId}": {
      "get": {
        "tags": [
          "competency"
        ],
        "summary": "Query for competencies",
        "description": "Query for competencies",
        "operationId": "retrieveCompetenciesByCourse",
        "responses": {
          "200": {
            "description": "Query result for competencies.",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/Competency"
                  }
                }
              }
            }
          },
          "400": {
            "description": "Invalid input"
          }
        },
        "parameters": [
          {
            "in": "path",
            "name": "courseId",
            "description": "Filter competencies by course",
            "required": true,
            "schema": {
              "$ref": "#/components/schemas/CourseId"
            }
          }
        ]
      }
    },
    "/courseCompetency": {
      "post": {
        "tags": [
          "relation"
        ],
        "summary": "Add a new course and competency relationship",
        "description": "Add a new course and competency relationship",
        "operationId": "addCourseCompetency",
        "responses": {
          "200": {
            "description": "Course competency relationship was added successfully.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/CourseCompetency"
                }
              }
            }
          },
          "400": {
            "description": "Invalid input"
          }
        },
        "requestBody": {
          "description": "Add a new course",
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CourseCompetencyWithoutId"
              }
            }
          }
        }
      }
    },
    "/course/{courseName}/extract": {
      "post": {
        "tags": [
          "course",
          "relation"
        ],
        "summary": "Add a new course and extract its competencies",
        "description": "Add a new course and extract its competencies and insert them into the db",
        "operationId": "addCourseExtract",
        "parameters": [
          {
            "in": "path",
            "name": "courseName",
            "description": "Name of course to be added",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Course was added successfully.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/CourseCompetency"
                }
              }
            }
          },
          "400": {
            "description": "Invalid input"
          }
        }
      }
    },
    "/initialize": {
      "post": {
        "tags": [
          "competency"
        ],
        "summary": "Initialize the database with EU-ESCO competencies",
        "description": "Initialize the database with EU-ESCO competencies",
        "operationId": "initialize",
        "responses": {
          "200": {
            "description": "Database and Store have been initialized successfully"
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "Course": {
        "properties": {
          "id": {
            "type": "integer"
          },
          "name": {
            "type": "string"
          },
          "body": {
            "type": "string"
          }
        }
      },
      "CourseId": {
        "properties": {
          "course_id": {
            "type": "integer"
          }
        }
      },
      "CourseBody": {
        "properties": {
          "course_body": {
            "type": "string"
          }
        }
      },
      "CompetencyBody": {
        "properties": {
          "competency_body": {
            "type": "string"
          }
        }
      },
      "Competency": {
        "properties": {
          "id": {
            "type": "integer"
          },
          "name": {
            "type": "string"
          },
          "body": {
            "type": "string"
          }
        }
      },
      "CompetencyId": {
        "properties": {
          "competency_id": {
            "type": "integer"
          }
        }
      },
      "CourseCompetency": {
        "properties": {
          "course_id": {
            "type": "integer"
          },
          "course_name": {
            "type": "string"
          },
          "course_body": {
            "type": "string"
          },
          "competency_id": {
            "type": "integer"
          },
          "competency_name": {
            "type": "string"
          },
          "competency_body": {
            "type": "string"
          }
        }
      },
      "CourseCompetencyWithoutId": {
        "properties": {
          "course_name": {
            "type": "string"
          },
          "course_body": {
            "type": "string"
          },
          "competency_name": {
            "type": "string"
          },
          "competency_body": {
            "type": "string"
          }
        }
      }
    }
  }
}