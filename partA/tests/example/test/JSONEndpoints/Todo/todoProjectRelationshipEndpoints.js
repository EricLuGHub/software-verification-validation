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

chai.use(chaiHttp);
chai.use(deepEqualInAnyOrder);

describe("/todos/:id/tasksof and /todos/:id/tasksof/:id endpoint API Calls - JSON", function () {
  beforeEach(async function () {
    child_process.spawn("java", ["-jar", "runTodoManagerRestAPI-1.5.5.jar"]);

    let serverReady = false;
    while (!serverReady) {
      try {
        await chai.request(host).get(todosEndpoint);
        serverReady = true;
      } catch (err) {}
    }
  });

  afterEach(async function () {
    try {
      await chai.request(host).get("/shutdown");
    } catch (err) {}
  });

  it("HEAD /todos/:id/tasksof - Return headers for the project items related to todo with existing given id - Capability", async function () {
    const todoID = 1;
    const response = await chai
      .request(host)
      .head(`${todosEndpoint}/${todoID}/${todoProjRelationship}`);
    expect(response).to.have.status(200);
  });

  it("HEAD /todos/:id/tasksof - Return headers for the project items related to todo with non-existing given id - BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN ERROR CODE 404
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 200
    const todoID = 40;
    const response = await chai
      .request(host)
      .head(`${todosEndpoint}/${todoID}/${todoProjRelationship}`);
    expect(response).to.have.status(200);
  });

  it("GET /todos/:id/tasksof - Returns projects items related to todo w/ existing given id - Capability", async function () {
    const todoID = 2;
    const response = await chai
      .request(host)
      .get(`${todosEndpoint}/${todoID}/${todoProjRelationship}`);
    const expected = {
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
          ],
        },
      ],
    };

    expect(response).to.have.status(200);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("GET /todos/:id/tasksof - Returns projects items related to todo w/ non-existing given id - BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN ERROR CODE 404 AND ERROR MESSAGE SINCE TODO DOES NOT EXIST
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 200 AND LIST INCLUDING PROJECT OF ID 1 REPEATED TWICE
    const todoID = 40;
    const response = await chai
      .request(host)
      .get(`${todosEndpoint}/${todoID}/${todoProjRelationship}`);
    const expected = {
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
          ],
        },
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
          ],
        },
      ],
    };

    expect(response).to.have.status(200);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("POST /todos/:id/tasksof - Create relationship between specified existing todo and existing project instance - Capability", async function () {
    const todoID = 2;
    const body = {
      id: "1",
    };
    const response = await chai
      .request(host)
      .post(`${todosEndpoint}/${todoID}/${todoProjRelationship}`)
      .send(body);
    expect(response).to.have.status(201);

    // VERIFYING DATA CHANGES AS EXPECTED BASED ON API CALL
    const createdRelationship = await chai
      .request(host)
      .get(`${todosEndpoint}/${todoID}/${todoProjRelationship}`);
    const expected = {
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
          ],
        },
      ],
    };

    expect(createdRelationship).to.have.status(200);
    expect(createdRelationship.body).to.deep.equalInAnyOrder(expected);
  });

  it("POST /todos/:id/tasksof - Create relationship between specified NON-existing todo and existing project instance - Error Case", async function () {
    const todoID = 40;
    const body = {
      id: "1",
    };
    const expected = {
      errorMessages: [
        `Could not find parent thing for relationship todos/${todoID}/tasksof`,
      ],
    };
    const response = await chai
      .request(host)
      .post(`${todosEndpoint}/${todoID}/${todoProjRelationship}`)
      .send(body);
    expect(response).to.have.status(404);
    expect(response.body).to.deep.equal(expected);
  });

  it("DELETE /todos/:id/tasksof/:id - Delete existing relationship instance between todo and project - Capability", async function () {
    const todoID = 2;
    const projID = 1;
    const response = await chai
      .request(host)
      .delete(`${todosEndpoint}/${todoID}/${todoProjRelationship}/${projID}`);
    expect(response).to.have.status(200);

    // VERIFYING DATA CHANGES AS EXPECTED BASED ON API CALL
    const projRelationshipsOfTodo = await chai
      .request(host)
      .get(`${todosEndpoint}/${todoID}/${todoProjRelationship}`);
    const expected = {
      projects: [],
    };

    expect(projRelationshipsOfTodo).to.have.status(200);
    expect(projRelationshipsOfTodo.body).to.deep.equal(expected);
  });

  it("DELETE /todos/:id/tasksof/:id - Delete non-existing relationship instance between todo and project (eg after it has already been deleted)- Error Case", async function () {
    const todoID = 2;
    const projID = 1;
    const response = await chai
      .request(host)
      .delete(`${todosEndpoint}/${todoID}/${todoProjRelationship}/${projID}`);
    expect(response).to.have.status(200);

    // VERIFYING DATA CHANGES AS EXPECTED BASED ON API CALL
    const secondAttemptResponse = await chai
      .request(host)
      .delete(`${todosEndpoint}/${todoID}/${todoProjRelationship}/${projID}`);
    const expected = {
      errorMessages: [
        `Could not find any instances with todos/${todoID}/tasksof/${projID}`,
      ],
    };
    expect(secondAttemptResponse.body).to.deep.equal(expected);
    expect(secondAttemptResponse).to.have.status(404);
  });

  it("Bidirectionality of POST /todos/:id/tasksof - Capability", async function () {
    const body = {
      title: "Important Errands and Tasks",
      completed: false,
      active: false,
      description: "Need to be done this month",
    };

    // CREATE NEW PROJECT TO MAKE A RELATIONSHIP
    const projCreated = await chai
      .request(host)
      .post(`${projectsEndpoint}`)
      .send(body);
    expect(projCreated).to.have.status(201);

    const todoID = 1;
    const projIDBody = {
      id: projCreated.body.id,
    };

    // CREATE TODO-PROJECT RELATIONSHIP
    const response = await chai
      .request(host)
      .post(`${todosEndpoint}/${todoID}/${todoProjRelationship}`)
      .send(projIDBody);
    expect(response).to.have.status(201);

    // VERIFYING TODO-PROJECT SIDE OF RELATIONSHIP (SUCCESS - EXISTENT)
    const createdRelationship = await chai
      .request(host)
      .get(`${todosEndpoint}/${todoID}/${todoProjRelationship}`);
    const expected = {
      projects: [
        {
          id: projIDBody.id,
          title: "Important Errands and Tasks",
          completed: "false",
          active: "false",
          description: "Need to be done this month",
          tasks: [
            {
              id: "1",
            },
          ],
        },
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
          ],
        },
      ],
    };
    expect(createdRelationship).to.have.status(200);
    expect(createdRelationship.body).to.deep.equalInAnyOrder(expected);

    // VERIFYING PROJECT-TODO SIDE OF RELATIONSHIP (SUCCESS - EXISTENT)
    const projTodoRelationships = await chai
      .request(host)
      .get(
        `/${projectsEndpoint}/${projCreated.body.id}/${projTodoRelationship}`
      );
    const expectedProjTodoRelationships = {
      todos: [
        {
          id: "1",
          title: "scan paperwork",
          doneStatus: "false",
          description: "",
          categories: [
            {
              id: "1",
            },
          ],
          tasksof: [
            {
              id: projCreated.body.id,
            },
            {
              id: "1",
            },
          ],
        },
      ],
    };
    expect(projTodoRelationships).to.have.status(200);
    expect(projTodoRelationships.body).to.deep.equalInAnyOrder(
      expectedProjTodoRelationships
    );
  });

  it("Bidirectionality of DELETE /todos/:id/tasksof/:id - Capability", async function () {
    const todoID = 1;
    const projID = 1;

    // DELETE EXISTING TODO-PROJECT RELATIONSHIP BETWEEN TODO W/ ID 1 AND PROJECT W/ ID 1
    const response = await chai
      .request(host)
      .delete(`${todosEndpoint}/${todoID}/${todoProjRelationship}/${projID}`);
    expect(response).to.have.status(200);

    // CHECK DELETION OF RELATIONSHIP FROM TODO SIDE (SUCCESS)
    const todoProjRelationships = await chai
      .request(host)
      .get(`${todosEndpoint}/${todoID}/${todoProjRelationship}`);
    const removedProject = {
      id: "1",
      title: "Office Work",
      completed: "false",
      active: "false",
      description: "",
      tasks: [
        {
          id: "1",
        },
        {
          id: "2",
        },
      ],
    };
    expect(todoProjRelationships).to.have.status(200);
    expect(todoProjRelationships.body).to.not.deep.include(removedProject);

    // CHECK DELETION OF RELATIONSHIP FROM PROJECT SIDE (SUCCESS)
    const projTodoRelationships = await chai
      .request(host)
      .get(`${projectsEndpoint}/${projID}/${projTodoRelationship}`);
    const removedTodo = {
      id: "1",
      title: "scan paperwork",
      doneStatus: "false",
      description: "",
      categories: [
        {
          id: "1",
        },
      ],
      tasksof: [
        {
          id: "1",
        },
      ],
    };
    expect(projTodoRelationships).to.have.status(200);
    expect(projTodoRelationships.body).to.not.deep.include(removedTodo);
  });
});
