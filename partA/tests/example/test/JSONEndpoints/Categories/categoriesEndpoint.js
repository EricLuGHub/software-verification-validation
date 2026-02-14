const expect = require("chai").expect;
const child_process = require("child_process");
const chai = require("chai");
const chaiHttp = require("chai-http");
const testConstants = require("../../testConstants.js");
const deepEqualInAnyOrder = require("deep-equal-in-any-order");

const host = testConstants.host;
const categoriesEndpoint = testConstants.categsEndpoint;

chai.use(chaiHttp);
chai.use(deepEqualInAnyOrder);

describe("/Categories endpoint API Calls - JSON", function () {
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

  afterEach(async function () {
    try {
      await chai.request(host).get("/shutdown");
    } catch (err) {}
  });

  it("GET /categories - Returns all categories in memory - Capability", async function () {
    const response = await chai.request(host).get(categoriesEndpoint);
    const expected = {
      categories: [
        {
          id: "2",
          title: "Home",
          description: "",
        },
        {
          id: "1",
          title: "Office",
          description: "",
        },
      ],
    };

    expect(response).to.have.status(200);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("POST /categories - Create a category w/out ID and with title- Capability", async function () {
    const body = {
      title: "University",
      description: "",
    };
    const response = await chai
      .request(host)
      .post(categoriesEndpoint)
      .send(body);
    const expected = {
      id: "3",
      title: "University",
      description: "",
    };
    expect(response).to.have.status(201);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("POST /categories - Create a category w/out ID and w/out title- Error Case", async function () {
    const body = {
      title: "",
      description: "Studying",
    };
    const response = await chai
      .request(host)
      .post(categoriesEndpoint)
      .send(body);
    const expected = {
      errorMessages: ["Failed Validation: title : can not be empty"],
    };
    expect(response).to.have.status(400);
    expect(response.body).to.deep.equal(expected);
  });

  it("HEAD /categories - Return header for /categories - Capability", async function () {
    const response = await chai.request(host).head(categoriesEndpoint);
    expect(response).to.have.status(200);
  });
});
