const expect = require("chai").expect;
const child_process = require("child_process");
const chai = require("chai");
const chaiHttp = require("chai-http");
const testConstants = require("../../../testConstants.js");
const deepEqualInAnyOrder = require("deep-equal-in-any-order");

const host = testConstants.host;
const todosEndpoint = testConstants.todosEndpoint;
const categoriesRelationship = testConstants.categoriesRelationship;

chai.use(chaiHttp);
chai.use(deepEqualInAnyOrder);

describe("UNDOCUMENTED ENDPOINT: GET /todos/categories - JSON", function () {
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

  it("Returns a list of categories", async function () {
    const expected = {
      categories: [
        {
          id: "1",
          title: "Office",
          description: "",
        },
      ],
    };

    const response = await chai
      .request(host)
      .get(`${todosEndpoint}/${categoriesRelationship}`);
    expect(response).to.have.status(200);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });
});
