import jwt from 'jsonwebtoken';
import { GlobalEntity } from '@/types';

function getExpiration(token: string) {
  const decodedToken: any = jwt.decode(token);
  return decodedToken.exp;
}

export default {
  entitiesNames: (state: any) => () => state.entities.map((element: GlobalEntity): string => element.entity),

  entityColor: (state: any) => (entity: string) => state.entities.find((e: any) => e.entity === entity)?.color,

  isLoggedIn: (state: any) => () => (state.token !== '' && getExpiration(state.token) >= new Date().getTime() / 1000),

  authToken: (state: any) => () => state.token,
};
