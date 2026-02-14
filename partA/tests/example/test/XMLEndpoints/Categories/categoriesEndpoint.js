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

describe("/categories endpoint API Calls - XML", function () {
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

  it("POST /categories - Create a category w/out ID and with title - Capability", async function () {
    const body = `<category>
            <title>University</title>
            <description></description>   
        </category>`;
    const response = await chai
      .request(host)
      .post(categoriesEndpoint)
      .set("Content-Type", "application/xml")
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
    const body = `<category>
            <title></title>
            <description>Meeting for 429 group</description>   
        </category>`;

    const response = await chai
      .request(host)
      .post(categoriesEndpoint)
      .set("Content-Type", "application/xml")
      .send(body);
    const expected = {
      errorMessages: ["Failed Validation: title : can not be empty"],
    };
    expect(response).to.have.status(400);
    expect(response.body).to.deep.equal(expected);
  });

  it("HEAD /categories - Return header for /categories - Capability", async function () {
    const response = await chai
      .request(host)
      .head(categoriesEndpoint)
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(200);
  });
});
