const expect = require("chai").expect;
const child_process = require("child_process");
const chai = require("chai");
const chaiHttp = require("chai-http");
const testConstants = require("../../testConstants.js");
const deepEqualInAnyOrder = require("deep-equal-in-any-order");

const host = testConstants.host;
const categoriesEndpoint = testConstants.categsEndpoint;
const categTodosRelationship = testConstants.categTodosRelationship;
const todosEndpoint = testConstants.todosEndpoint;
const categoriesRelationship = testConstants.categoriesRelationship;
const validID = 1;
const invalidID = 20;

chai.use(chaiHttp);
chai.use(deepEqualInAnyOrder);

describe("/categories/:id/todos and /categories/:id/todos/:id endpoint API Calls - JSON", function () {
  beforeEach(async function () {
    child_process.spawn("java", ["-jar", "runTodoManagerRestAPI-1.5.5.jar"]);
    let serverReady = false;
    while (!serverReady) {
      try {
        await chai.request(host).get(categoriesEndpoint);
        serverReady = true;
      } catch (err) {}
    }
  });

  beforeEach(async () => {
    try {
      await chai
        .request(host)
        .post(`${categoriesEndpoint}/${validID}/${categTodosRelationship}`)
        .send({
          id: "2",
        });
    } catch (err) {}
  });

  afterEach(async function () {
    try {
      await chai.request(host).get("/shutdown");
    } catch (err) {}
  });

  it("GET /categories/:id/todos - Returns todo items related to category w/ existing given id - Capability", async function () {
    const response = await chai
      .request(host)
      .get(`${categoriesEndpoint}/${validID}/${categTodosRelationship}`);
    const expected = {
      todos: [
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

  it("GET /categories/:id/todos - Returns todo items related to category w/ non-existing given id - BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN ERROR CODE 404 AND ERROR MESSAGE SINCE CATEGORY DOES NOT EXIST
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 200 AND LIST INCLUDING TODOS WHICH SHOULDNT BE THERE
    const response = await chai
      .request(host)
      .get(`${categoriesEndpoint}/${invalidID}/${categTodosRelationship}`);
    //EXPECTED an error message but this is a bug
    const expected = {
      todos: [
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

  it("HEAD /categories/:id/todos - Return headers for the todo items related to category, with existing given id - Capability", async function () {
    const response = await chai
      .request(host)
      .head(`${categoriesEndpoint}/${validID}/${categTodosRelationship}`);
    expect(response).to.have.status(200);
  });

  it("HEAD /categories/:id/todos - Return headers for the todo items related to non-existing category - BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN ERROR CODE 404
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 200
    const response = await chai
      .request(host)
      .head(`${categoriesEndpoint}/${invalidID}/${categTodosRelationship}`);
    expect(response).to.have.status(200);
  });

  it("POST /categories/:id/todos - Create relationship between specified existing category and existing todo instance - Capability", async function () {
    const body = {
      id: "1",
    };
    const response = await chai
      .request(host)
      .post(`${categoriesEndpoint}/${validID}/${categTodosRelationship}`)
      .send(body);
    expect(response).to.have.status(201);

    //Verifying that the relationship persists
    const relationship = await chai
      .request(host)
      .get(`${categoriesEndpoint}/${validID}/${categTodosRelationship}`);
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

  it("POST /categories/:id/todos - Create relationship between specified nonexistent category and existing todo instance - Error Case", async function () {
    const body = {
      id: "1",
    };
    const expected = {
      errorMessages: [
        `Could not find parent thing for relationship categories/${invalidID}/todos`,
      ],
    };
    const response = await chai
      .request(host)
      .post(`${categoriesEndpoint}/${invalidID}/${categTodosRelationship}`)
      .send(body);
    expect(response).to.have.status(404);
    expect(response.body).to.deep.equal(expected);
  });

  it("DELETE /categories/:id/todos - Delete existing relationship instance between category and todo - Capability", async function () {
    const todoID = 2;
    const response = await chai
      .request(host)
      .delete(
        `${categoriesEndpoint}/${validID}/${categTodosRelationship}/${todoID}`
      );
    expect(response).to.have.status(200);

    // Veryfying deletion through get request
    const relationship = await chai
      .request(host)
      .get(`${categoriesEndpoint}/${validID}/${categTodosRelationship}`);
    const expected = {
      todos: [],
    };

    expect(relationship).to.have.status(200);
    expect(relationship.body).to.deep.equal(expected);
  });

  it("DELETE /categories/:id/todos/:id - Delete non-existing relationship instance between category and todo - Error Case", async function () {
    const todoID = 20;
    const response = await chai
      .request(host)
      .delete(
        `${categoriesEndpoint}/${validID}/${categTodosRelationship}/${todoID}`
      );

    const expected = {
      errorMessages: [
        `Could not find any instances with categories/${validID}/todos/${todoID}`,
      ],
    };
    expect(response).to.have.status(404);
    expect(response.body).to.deep.equal(expected);
  });

  it("POST /categories/:id/tasks - Create relationship between specified existing category and existing todo instance - Capability", async function () {
    const body = {
      id: "1",
    };

    const response = await chai
      .request(host)
      .post(`${categoriesEndpoint}/${validID}/${categTodosRelationship}`)
      .send(body);
    expect(response).to.have.status(201);

    //Checking that the relationship exists from category=>todo
    const relationship = await chai
      .request(host)
      .get(`${categoriesEndpoint}/${validID}/${categTodosRelationship}`);
    const expected = {
      todos: [
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
    expect(relationship).to.have.status(200);
    expect(relationship.body).to.deep.equalInAnyOrder(expected);
    //Checking if todo=>category relationship is created (SUCCESS - EXISTS)
    const todoCategoryRel = await chai
      .request(host)
      .get(`${todosEndpoint}/${body.id}/${categoriesRelationship}`);
    const expectedRel = {
      categories: [
        {
          id: "1",
          title: "Office",
          description: "",
          todos: [
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
    expect(todoCategoryRel).to.have.status(200);
    expect(todoCategoryRel.body).to.deep.equalInAnyOrder(expectedRel);
  });

  it("DELETE /categories/:id/todos/:id - Delete existing relationship instance between category and todo - Capability", async function () {
    const todoID = 2;
    const response = await chai
      .request(host)
      .delete(
        `${categoriesEndpoint}/${validID}/${categTodosRelationship}/${todoID}`
      );
    expect(response).to.have.status(200);
    // Verifying deletion through get request
    const relationship = await chai
      .request(host)
      .get(`${categoriesEndpoint}/${validID}/${categTodosRelationship}`);
    const expected = {
      todos: [],
    };

    expect(relationship).to.have.status(200);
    expect(relationship.body).to.deep.equal(expected);
    //Checking if todo=>category relationship is deleted (SUCCESS - DELETES)
    const todoCategoryRel = await chai
      .request(host)
      .get(`${todosEndpoint}/${todoID}/${categoriesRelationship}`);
    const expectedProj = {
      categories: [],
    };
    expect(todoCategoryRel).to.have.status(200);
    expect(todoCategoryRel.body).to.deep.equalInAnyOrder(expectedProj);
  });
});
