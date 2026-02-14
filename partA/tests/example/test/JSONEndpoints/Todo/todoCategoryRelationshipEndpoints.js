const expect = require("chai").expect;
const child_process = require("child_process");
const chai = require("chai");
const chaiHttp = require("chai-http");
const testConstants = require("../../testConstants.js");
const deepEqualInAnyOrder = require("deep-equal-in-any-order");

const host = testConstants.host;
const todosEndpoint = testConstants.todosEndpoint;
const categoriesRelationship = testConstants.categoriesRelationship;
const categoriesEndpoint = testConstants.categsEndpoint;

chai.use(chaiHttp);
chai.use(deepEqualInAnyOrder);

describe("/todos/:id/categories and /todos/:id/categories/:id endpoint functioning API Calls - JSON", function () {
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

  it("HEAD /todos/:id/categories - Return headers for the category items related to todo, with existing given id - Capability", async function () {
    const todoID = 1;
    const response = await chai
      .request(host)
      .head(`${todosEndpoint}/${todoID}/${categoriesRelationship}`);
    expect(response).to.have.status(200);
  });

  it("HEAD /todos/:id/categories - Return headers for the category items related to todo, w/ given non-existing id - BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN ERROR CODE 404
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 200
    const todoID = 40;
    const response = await chai
      .request(host)
      .head(`${todosEndpoint}/${todoID}/${categoriesRelationship}`);
    expect(response).to.have.status(200);
  });

  it("GET /todos/:id/categories - Returns category items related to todo w/ existing given id - Capability", async function () {
    const todoID = 1;
    const response = await chai
      .request(host)
      .get(`${todosEndpoint}/${todoID}/${categoriesRelationship}`);
    const expected = {
      categories: [
        {
          id: "1",
          title: "Office",
          description: "",
        },
      ],
    };

    expect(response).to.have.status(200);
    expect(response.body).to.deep.equal(expected);
  });

  it("GET /todos/:id/categories - Returns category items related to todo w/ non-existing given id - BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN ERROR CODE 404 AND ERROR MESSAGE SINCE TODO DOES NOT EXIST
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 200 AND LIST INCLUDING CATEGORY OF ID 1
    const todoID = 40;
    const response = await chai
      .request(host)
      .get(`${todosEndpoint}/${todoID}/${categoriesRelationship}`);
    const expected = {
      categories: [
        {
          id: "1",
          title: "Office",
          description: "",
        },
      ],
    };

    expect(response).to.have.status(200);
    expect(response.body).to.deep.equal(expected);
  });

  it("POST /todos/:id/categories - Create relationship between specified existing todo and existing category instance - Capability", async function () {
    const todoID = 2;
    const body = {
      id: "2",
    };
    const response = await chai
      .request(host)
      .post(`${todosEndpoint}/${todoID}/${categoriesRelationship}`)
      .send(body);
    expect(response).to.have.status(201);

    // VERIFYING DATA CHANGES AS EXPECTED BASED ON API CALL
    const createdRelationship = await chai
      .request(host)
      .get(`${todosEndpoint}/${todoID}/${categoriesRelationship}`);
    const expected = {
      categories: [
        {
          id: "2",
          title: "Home",
          description: "",
        },
      ],
    };
    expect(createdRelationship).to.have.status(200);
    expect(createdRelationship.body).to.deep.equalInAnyOrder(expected);
  });

  it("POST /todos/:id/categories - Create relationship between specified NON-existing todo and existing category instance - Error Case", async function () {
    const todoID = 40;
    const body = {
      id: "2",
    };
    const expected = {
      errorMessages: [
        `Could not find parent thing for relationship todos/${todoID}/categories`,
      ],
    };
    const response = await chai
      .request(host)
      .post(`${todosEndpoint}/${todoID}/${categoriesRelationship}`)
      .send(body);
    expect(response).to.have.status(404);
    expect(response.body).to.deep.equal(expected);
  });

  it("DELETE /todos/:id/categories/:id - Delete existing relationship instance between todo and category - Capability", async function () {
    const todoID = 1;
    const categID = 1;
    const response = await chai
      .request(host)
      .delete(
        `${todosEndpoint}/${todoID}/${categoriesRelationship}/${categID}`
      );
    expect(response).to.have.status(200);

    // VERIFYING DATA CHANGES AS EXPECTED BASED ON API CALL
    const categRelationshipsOfTodo = await chai
      .request(host)
      .get(`${todosEndpoint}/${todoID}/${categoriesRelationship}`);
    const expected = {
      categories: [],
    };

    expect(categRelationshipsOfTodo).to.have.status(200);
    expect(categRelationshipsOfTodo.body).to.deep.equal(expected);
  });

  it("DELETE /todos/:id/categories/:id - Delete non-existing relationship instance between todo and category (eg after it has already been deleted)- Error Case", async function () {
    const todoID = 1;
    const categID = 1;
    const response = await chai
      .request(host)
      .delete(
        `${todosEndpoint}/${todoID}/${categoriesRelationship}/${categID}`
      );
    expect(response).to.have.status(200);

    const secondAttemptResponse = await chai
      .request(host)
      .delete(
        `${todosEndpoint}/${todoID}/${categoriesRelationship}/${categID}`
      );
    const expected = {
      errorMessages: [
        `Could not find any instances with todos/${todoID}/categories/${categID}`,
      ],
    };
    expect(secondAttemptResponse.body).to.deep.equal(expected);
    expect(secondAttemptResponse).to.have.status(404);
  });

  it("Bidirectionality of POST /todos/:id/categories - BUG", async function () {
    // EXPECTED BEHAVIOR: EXISTENT RELATIONSHIP ON BOTH TODO AND CATEGORY SIDE FOR BIDIRECTIONALITY TO BE SATISFIED
    // ACTUAL BEHAVIOR: UNIDIRECTIONAL RELATIONSHIP ON TODO SIDE ONLY
    const todoID = 2;
    const body = {
      id: "2",
    };
    const response = await chai
      .request(host)
      .post(`${todosEndpoint}/${todoID}/${categoriesRelationship}`)
      .send(body);
    expect(response).to.have.status(201);

    // VERIFYING TODO-CATEGORY SIDE OF RELATIONSHIP (SUCCESS - EXISTENT)
    const createdRelationship = await chai
      .request(host)
      .get(`${todosEndpoint}/${todoID}/${categoriesRelationship}`);
    const expected = {
      categories: [
        {
          id: "2",
          title: "Home",
          description: "",
        },
      ],
    };
    expect(createdRelationship).to.have.status(200);
    expect(createdRelationship.body).to.deep.equalInAnyOrder(expected);

    // VERIFYING CATEGORY-TODO SIDE OF RELATIONSHIP (BUG - NON-EXISTENT)
    const categTodoRelationships = await chai
      .request(host)
      .get(`${categoriesEndpoint}/${body.id}/${todosEndpoint}`);
    const expectedCategTodoRelationships = {
      todos: [],
    };
    expect(categTodoRelationships).to.have.status(200);
    expect(categTodoRelationships.body).to.deep.equal(
      expectedCategTodoRelationships
    );
  });
});
