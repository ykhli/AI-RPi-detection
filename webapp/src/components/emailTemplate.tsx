import * as React from "react";
import { Img } from "@react-email/img";

interface EmailTemplateProps {
  url: string;
}

export const EmailTemplate: React.FC<Readonly<EmailTemplateProps>> = ({
  url,
}) => (
  <div>
    <h1>Hello! Your cat just jumped on your table again:</h1>
    <Img src={url} alt="Cat" width="3200" height="500" />
  </div>
);
