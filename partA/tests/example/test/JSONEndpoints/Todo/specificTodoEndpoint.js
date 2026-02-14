const expect = require("chai").expect;
const child_process = require("child_process");
const chai = require("chai");
const chaiHttp = require("chai-http");
const testConstants = require("../../testConstants.js");
const deepEqualInAnyOrder = require("deep-equal-in-any-order");

const host = testConstants.host;
const todosEndpoint = testConstants.todosEndpoint;

chai.use(chaiHttp);
chai.use(deepEqualInAnyOrder);

describe("/todos/:id endpoint API Calls - JSON", function () {
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

  it("GET /todos/:id - Returns todo with specific existing passed id - Capability", async function () {
    const todoID = 1;
    const response = await chai.request(host).get(`${todosEndpoint}/${todoID}`);
    const expected = {
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
              id: "1",
            },
          ],
        },
      ],
    };

    expect(response).to.have.status(200);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("GET /todos/:id - Returns todo with specific non-existing passed id - Error Case", async function () {
    const todoID = 45;
    const response = await chai.request(host).get(`${todosEndpoint}/${todoID}`);
    const expected = {
      errorMessages: [`Could not find an instance with todos/${todoID}`],
    };

    expect(response).to.have.status(404);
    expect(response.body).to.deep.equal(expected);
  });

  it("POST /todos - Creates a new TODO with fields passed through body - Capability", async function () {
    const body = {
      title: "Wash Dishes",
      doneStatus: false,
      description: "Home Chore to be done",
    };
    const response = await chai
      .request(host)
      .post(`${todosEndpoint}`)
      .send(body);
    const expected = {
      id: "3",
      title: "Wash Dishes",
      doneStatus: "false",
      description: "Home Chore to be done",
    };

    expect(response).to.have.status(201);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("POST /todos/:id - Updates an existing TODO with fields passed through body - Capability", async function () {
    const todoID = 1;
    const body = {
      doneStatus: true,
      description: "all paperwork scanned",
    };
    const response = await chai
      .request(host)
      .post(`${todosEndpoint}/${todoID}`)
      .send(body);
    const expected = {
      id: "1",
      title: "scan paperwork",
      doneStatus: "true",
      description: "all paperwork scanned",
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

    expect(response).to.have.status(200);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("POST /todos/:id - Update a non-existing TODO with fields passed through body - Error Case", async function () {
    const todoID = 45;
    const body = {
      doneStatus: true,
      description: "all paperwork scanned",
    };
    const response = await chai
      .request(host)
      .post(`${todosEndpoint}/${todoID}`)
      .send(body);
    const expected = {
      errorMessages: [
        `No such todo entity instance with GUID or ID ${todoID} found`,
      ],
    };

    expect(response).to.have.status(404);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("HEAD /todos - Return headers for todo w/ existing specified given id - Capability", async function () {
    const todoID = 1;
    const response = await chai
      .request(host)
      .head(`${todosEndpoint}/${todoID}`);
    expect(response).to.have.status(200);
  });

  it("HEAD /todos - Return headers for todo w/ non-existing specified given id  - Error Case", async function () {
    const todoID = 45;
    const response = await chai
      .request(host)
      .head(`${todosEndpoint}/${todoID}`);
    expect(response).to.have.status(404);
  });

  it("PUT /todos/:id - Update an existing TODO with fields passed through body - Capability", async function () {
    const todoID = 1;
    const body = {
      title: "Wash Dog",
      doneStatus: false,
      description: "giving him a bath",
    };
    const response = await chai
      .request(host)
      .put(`${todosEndpoint}/${todoID}`)
      .send(body);
    const expected = {
      id: "1",
      title: "Wash Dog",
      doneStatus: "false",
      description: "giving him a bath",
    };

    expect(response).to.have.status(200);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("PUT /todos/:id - Update a non-existing TODO with fields passed through body - Error Case", async function () {
    const todoID = 45;
    const body = {
      title: "Wash Dog",
      doneStatus: false,
      description: "giving him a bath",
    };
    const response = await chai
      .request(host)
      .put(`${todosEndpoint}/${todoID}`)
      .send(body);
    const expected = {
      errorMessages: [`Invalid GUID for ${todoID} entity todo`],
    };

    expect(response).to.have.status(404);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("DELETE /todos/:id - Delete TODO w/ specified existing id - Capability", async function () {
    const todoID = 1;
    const response = await chai
      .request(host)
      .delete(`${todosEndpoint}/${todoID}`);
    expect(response).to.have.status(200);

    // VERIFYING DATA CHANGES AS EXPECTED BASED ON API CALL
    const projRelationshipsOfTodo = await chai
      .request(host)
      .get(`${todosEndpoint}/${todoID}`);
    const expected = {
      errorMessages: [`Could not find an instance with todos/${todoID}`],
    };

    expect(projRelationshipsOfTodo).to.have.status(404);
    expect(projRelationshipsOfTodo.body).to.deep.equal(expected);
  });

  it("DELETE /todos/:id - Deletes TODO w/ specified non-existing id - Error Case", async function () {
    const todoID = 45;
    const response = await chai
      .request(host)
      .delete(`${todosEndpoint}/${todoID}`);
    const expected = {
      errorMessages: [`Could not find any instances with todos/${todoID}`],
    };

    expect(response).to.have.status(404);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("DELETE /todos/:id - Delete TODO using existing ID that was already deleted - Error Case", async function () {
    const todoID = 1;
    const response = await chai
      .request(host)
      .delete(`${todosEndpoint}/${todoID}`);
    expect(response).to.have.status(200);

    // VERIFYING DATA CHANGES AS EXPECTED BASED ON API CALL
    const secondAttemptResponse = await chai
      .request(host)
      .delete(`${todosEndpoint}/${todoID}`);
    const expected = {
      errorMessages: [`Could not find any instances with todos/${todoID}`],
    };

    expect(secondAttemptResponse).to.have.status(404);
    expect(secondAttemptResponse.body).to.deep.equalInAnyOrder(expected);
  });
});
