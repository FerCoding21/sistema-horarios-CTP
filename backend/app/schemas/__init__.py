from app.schemas.base         import ResponseBase
from app.schemas.especialidad import (EspecialidadCreate, EspecialidadUpdate,
                                       EspecialidadResponse)
from app.schemas.materia      import (MateriaCreate, MateriaUpdate, MateriaResponse)
from app.schemas.usuario      import (LoginRequest, TokenResponse,
                                       UsuarioCreate, UsuarioResponse,
                                       CambiarPasswordRequest)
from app.schemas.grupo        import (GrupoCreate, GrupoUpdate, GrupoResponse)
