import {
  CognitoIdentityProviderClient,
  InitiateAuthCommand,
  SignUpCommand,
  ConfirmSignUpCommand,
} from "@aws-sdk/client-cognito-identity-provider";
import config from "./config.json"; 

const cognitoClient = new CognitoIdentityProviderClient({
  region: config.region,
});

export const signIn = async (username, password) => {
  const params = {
    AuthFlow: "USER_PASSWORD_AUTH",
    ClientId: config.clientId,
    AuthParameters: {
      USERNAME: username,
      PASSWORD: password,
    },
  };

  try {
    const command = new InitiateAuthCommand(params);
    const { AuthenticationResult } = await cognitoClient.send(command);

    if (AuthenticationResult) {
      sessionStorage.setItem("idToken", AuthenticationResult.IdToken || "");
      sessionStorage.setItem("accessToken", AuthenticationResult.AccessToken || "");
      sessionStorage.setItem("refreshToken", AuthenticationResult.RefreshToken || "");
      return AuthenticationResult;
    } else {
      throw new Error("Authentication failed");
    }
  } catch (error) {
    console.error("Error during sign in:", error);
    throw error;
  }
};

export const signOut = () => {
  sessionStorage.removeItem("idToken");
  sessionStorage.removeItem("accessToken");
  sessionStorage.removeItem("refreshToken");
};

export const signUp = async (email, password, firstName, lastName) => {
  const params = {
    ClientId: config.clientId,
    Username: email,
    Password: password,
    UserAttributes: [
      {
        Name: "email",
        Value: email,
      },
      { Name: "given_name", Value: firstName },
      { Name: "family_name", Value: lastName },
    ],
  };

  try {
    const command = new SignUpCommand(params);
    const response = await cognitoClient.send(command);
    console.log("Sign up success:", response);
    return response;
  } catch (error) {
    console.error("Error signing up:", error);
    throw error;
  }
};

export const confirmSignUp = async (email, code) => {
  const params = {
    ClientId: config.clientId,
    Username: email,
    ConfirmationCode: code,
  };

  try {
    const command = new ConfirmSignUpCommand(params);
    const response = await cognitoClient.send(command);
    console.log("User confirmed successfully:", response);
    return response;
  } catch (error) {
    console.error("Error confirming signup:", error);
    throw error;
  }
};

