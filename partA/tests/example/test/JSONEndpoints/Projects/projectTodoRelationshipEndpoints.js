const expect = require("chai").expect;
const child_process = require("child_process");
const chai = require("chai");
const chaiHttp = require("chai-http");
const testConstants = require("../../testConstants.js");
const deepEqualInAnyOrder = require("deep-equal-in-any-order");

const host = testConstants.host;
const todosEndpoint = testConstants.todosEndpoint;
const projectsEndpoint = testConstants.projectsEndpoint;
const projTodoRelationship = testConstants.projTodoRelationship;
const todoProjRelationship = testConstants.todoProjRelationship;
const validID = 1;
const invalidID = 20;

chai.use(chaiHttp);
chai.use(deepEqualInAnyOrder);

describe("/projects/:id/tasks & /projects/:id/tasks/:id endpoint API Calls - JSON", function () {
  beforeEach(async function () {
    child_process.spawn("java", ["-jar", "runTodoManagerRestAPI-1.5.5.jar"]);

    let serverReady = false;
    while (!serverReady) {
      try {
        await chai.request(host).get(projectsEndpoint);
        serverReady = true;
      } catch (err) {}
    }
  });

  //Creating a new task to test project-task relationship
  beforeEach(async () => {
    let body = {
      title: "Gardening",
      doneStatus: false,
      description: "water the plants",
    };
    try {
      await chai.request(host).post(todosEndpoint).send(body);
    } catch (err) {}
  });

  afterEach(async function () {
    try {
      await chai.request(host).get("/shutdown");
    } catch (err) {}
  });

  it("GET /projects/:id/tasks - Returns tasks items related to project w/ existing given id - Capability", async function () {
    const response = await chai
      .request(host)
      .get(`${projectsEndpoint}/${validID}/${projTodoRelationship}`);
    const expected = {
      todos: [
        {
          id: "1",
          title: "scan paperwork",
          doneStatus: "false",
          description: "",
          tasksof: [
            {
              id: "1",
            },
          ],
          categories: [
            {
              id: "1",
            },
          ],
        },
        {
          id: "2",
          title: "file paperwork",
          doneStatus: "false",
          description: "",
          tasksof: [
            {
              id: "1",
            },
          ],
        },
      ],
    };

    expect(response).to.have.status(200);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("GET /projects/:id/tasks - Returns tasks items related to project w/ non-existing given id - BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN ERROR CODE 404 AND ERROR MESSAGE SINCE PROJECT DOES NOT EXIST
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 200 AND LIST INCLUDING TODOS OF ID 1 REPEATED TWICE
    const response = await chai
      .request(host)
      .get(`${projectsEndpoint}/${invalidID}/${projTodoRelationship}`);
    //EXPECTED an error message but this is a bug
    const expected = {
      todos: [
        {
          id: "1",
          title: "scan paperwork",
          doneStatus: "false",
          description: "",
          tasksof: [
            {
              id: "1",
            },
          ],
          categories: [
            {
              id: "1",
            },
          ],
        },
        {
          id: "2",
          title: "file paperwork",
          doneStatus: "false",
          description: "",
          tasksof: [
            {
              id: "1",
            },
          ],
        },
      ],
    };

    expect(response).to.have.status(200);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("HEAD /projects/:id/tasks - Return headers for the todo items related to project, with existing given id - Capability", async function () {
    const response = await chai
      .request(host)
      .head(`${projectsEndpoint}/${validID}/${projTodoRelationship}`);
    expect(response).to.have.status(200);
  });

  it("HEAD /projects/:id/tasks - Return headers for the todo items related to non-existing project,- BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN ERROR CODE 404
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 200
    const response = await chai
      .request(host)
      .head(`${projectsEndpoint}/${invalidID}/${projTodoRelationship}`);
    //Actual Expected status is 404
    expect(response).to.have.status(200);
  });

  it("POST /projects/:id/tasks - Create relationship between specified existing project and existing todo instance - Capability", async function () {
    const body = {
      id: "2",
    };
    const response = await chai
      .request(host)
      .post(`${projectsEndpoint}/${validID}/${projTodoRelationship}`)
      .send(body);
    expect(response).to.have.status(201);

    //Verifying that the relationship persists
    const relationship = await chai
      .request(host)
      .get(`${projectsEndpoint}/${validID}/${projTodoRelationship}`);
    const expected = {
      todos: [
        {
          id: "1",
          title: "scan paperwork",
          doneStatus: "false",
          description: "",
          tasksof: [
            {
              id: "1",
            },
          ],
          categories: [
            {
              id: "1",
            },
          ],
        },
        {
          id: "2",
          title: "file paperwork",
          doneStatus: "false",
          description: "",
          tasksof: [
            {
              id: "1",
            },
          ],
        },
      ],
    };
    expect(relationship).to.have.status(200);
    expect(relationship.body).to.deep.equalInAnyOrder(expected);
  });

  it("POST /projects/:id/tasks - Create relationship between specified non-existing project and existing todo instance - Error Case", async function () {
    const body = {
      id: "1",
    };
    const expected = {
      errorMessages: [
        `Could not find parent thing for relationship projects/${invalidID}/tasks`,
      ],
    };
    const response = await chai
      .request(host)
      .post(`${projectsEndpoint}/${invalidID}/${projTodoRelationship}`)
      .send(body);
    expect(response).to.have.status(404);
    expect(response.body).to.deep.equal(expected);
  });

  it("DELETE /projects/:id/tasks/:id - Delete existing relationship instance between project and todo - Capability", async function () {
    const todoID = 2;
    const response = await chai
      .request(host)
      .delete(
        `${projectsEndpoint}/${validID}/${projTodoRelationship}/${todoID}`
      );
    expect(response).to.have.status(200);

    // Veryfying deletion through get request
    const relationship = await chai
      .request(host)
      .get(`${projectsEndpoint}/${validID}/${projTodoRelationship}`);
    const expected = {
      todos: [
        {
          id: "1",
          title: "scan paperwork",
          doneStatus: "false",
          description: "",
          tasksof: [
            {
              id: "1",
            },
          ],
          categories: [
            {
              id: "1",
            },
          ],
        },
      ],
    };

    expect(relationship).to.have.status(200);
    expect(relationship.body).to.deep.equal(expected);
  });

  it("DELETE /todos/:id/tasks/:id - Delete non-existing relationship instance between project and todo- Error Case", async function () {
    const todoID = 20;
    const response = await chai
      .request(host)
      .delete(
        `${projectsEndpoint}/${validID}/${projTodoRelationship}/${todoID}`
      );

    const expected = {
      errorMessages: [
        `Could not find any instances with projects/${validID}/tasks/${todoID}`,
      ],
    };
    expect(response).to.have.status(404);
    expect(response.body).to.deep.equal(expected);
  });

  it("POST /projects/:id/tasks - Create relationship between specified non-existing project and existing todo instance - CAPABILITY", async function () {
    const body = {
      id: "3",
    };

    const response = await chai
      .request(host)
      .post(`${projectsEndpoint}/${validID}/${projTodoRelationship}`)
      .send(body);
    expect(response).to.have.status(201);

    //Checking that the relationship exists from projects=>todo
    const relationship = await chai
      .request(host)
      .get(`${projectsEndpoint}/${validID}/${projTodoRelationship}`);
    const expected = {
      todos: [
        {
          id: "1",
          title: "scan paperwork",
          doneStatus: "false",
          description: "",
          tasksof: [
            {
              id: "1",
            },
          ],
          categories: [
            {
              id: "1",
            },
          ],
        },
        {
          id: "2",
          title: "file paperwork",
          doneStatus: "false",
          description: "",
          tasksof: [
            {
              id: "1",
            },
          ],
        },
        {
          id: "3",
          title: "Gardening",
          doneStatus: "false",
          description: "water the plants",
          tasksof: [
            {
              id: "1",
            },
          ],
        },
      ],
    };
    expect(relationship).to.have.status(200);
    expect(relationship.body).to.deep.equalInAnyOrder(expected);

    //Checking if todo=>projects relationship is created (bidirectionality)
    const taskProjectRel = await chai
      .request(host)
      .get(`${todosEndpoint}/${body.id}/${todoProjRelationship}`);
    const expectedRel = {
      projects: [
        {
          id: "1",
          title: "Office Work",
          completed: "false",
          active: "false",
          description: "",
          tasks: [
            {
              id: "2",
            },
            {
              id: "1",
            },
            {
              id: "3",
            },
          ],
        },
      ],
    };
    expect(taskProjectRel).to.have.status(200);
    expect(taskProjectRel.body).to.deep.equalInAnyOrder(expectedRel);
  });

  it("DELETE /projects/:id/tasks/:id - Delete existing relationship instance between project and todo - Capability", async function () {
    const todoID = 2;
    const response = await chai
      .request(host)
      .delete(
        `${projectsEndpoint}/${validID}/${projTodoRelationship}/${todoID}`
      );
    expect(response).to.have.status(200);

    // Veryfying deletion through get request
    const relationship = await chai
      .request(host)
      .get(`${projectsEndpoint}/${validID}/${projTodoRelationship}`);
    const expected = {
      todos: [
        {
          id: "1",
          title: "scan paperwork",
          doneStatus: "false",
          description: "",
          tasksof: [
            {
              id: "1",
            },
          ],
          categories: [
            {
              id: "1",
            },
          ],
        },
      ],
    };

    expect(relationship).to.have.status(200);
    expect(relationship.body).to.deep.equal(expected);

    //Checking if todo=>projects relationship is deleted (bidirectionality)
    const taskProjectRel = await chai
      .request(host)
      .get(`${todosEndpoint}/${todoID}/${todoProjRelationship}`);
    const expectedProj = {
      projects: [],
    };

    expect(taskProjectRel).to.have.status(200);
    expect(taskProjectRel.body).to.deep.equalInAnyOrder(expectedProj);
  });
});
